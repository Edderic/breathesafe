# frozen_string_literal: true

# Controller with CRUD operations for Masks
class MasksController < ApplicationController
  skip_before_action :verify_authenticity_token

  SORT_COLUMN_MAP = {
    'probaFit' => 'proba_fit',
    'avgSealedFitFactor' => 'avg_sealed_fit_factor',
    'avgBreathabilityPa' => 'avg_breathability_pa',
    'uniqueFitTestersCount' => 'unique_fit_testers_count',
    'perimeterMm' => 'perimeter_mm',
    'uniqueInternalModelCode' => 'unique_internal_model_code',
    'fitTestCount' => 'fit_test_count'
  }.freeze
  DEFAULT_SORT_COLUMN = 'unique_internal_model_code'

  def create
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      mask = {}
    else
      hashed_mask_data = mask_data.to_hash
      hashed_mask_data[:author_id] = current_user.id

      mask = Mask.create(hashed_mask_data)

      if mask.errors.full_messages.empty?
        status = 201
        messages = []
      else
        status = 422
        messages = mask.errors.full_messages
        mask = {}
      end
    end

    to_render = {
      mask: mask,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def index
    permitted = params.permit(
      :page,
      :per_page,
      :search,
      :sort_by,
      :sort_order,
      :filter_color,
      :filter_style,
      :filter_strap_type,
      :filter_missing
    )

    page = permitted[:page].to_i.positive? ? permitted[:page].to_i : 1
    per_page = permitted[:per_page].to_i.positive? ? permitted[:per_page].to_i : 12
    search = permitted[:search].presence
    filter_color = permitted[:filter_color].presence
    filter_style = permitted[:filter_style].presence
    filter_strap_type = permitted[:filter_strap_type].presence
    filter_missing = permitted[:filter_missing].presence
    sort_param = permitted[:sort_by].presence
    sort_column = SORT_COLUMN_MAP.fetch(sort_param, DEFAULT_SORT_COLUMN)
    sort_order = permitted[:sort_order] == 'descending' ? :desc : :asc

    masks_query = Mask.all
    masks_query = masks_query.where('unique_internal_model_code ILIKE ?', "%#{search}%") if search
    masks_query = masks_query.where(style: filter_style) if filter_style && filter_style != 'none'
    masks_query = masks_query.where(strap_type: filter_strap_type) if filter_strap_type && filter_strap_type != 'none'
    masks_query = masks_query.where('colors @> ?', [filter_color].to_json) if filter_color && filter_color != 'none'

    mask_ids = masks_query.order(:id).pluck(:id)
    if mask_ids.empty?
      return render json: {
        masks: [],
        total_count: 0,
        page: page,
        per_page: per_page,
        messages: []
      }, status: :ok
    end
    mask_ids.size

    aggregated_masks = if current_user&.admin
                         Mask.with_admin_aggregations(mask_ids)
                       else
                         Mask.with_privacy_aggregations(mask_ids)
                       end
    mask_id_lookup = mask_ids.index_with { |_id| true }
    aggregated_masks.select! do |mask|
      mask_id_lookup[mask['id']] || mask_id_lookup[mask[:id]]
    end

    if filter_missing.present? && filter_missing != 'none'
      missing_filters = filter_missing.to_s.split(',').map(&:strip).reject(&:blank?)
      if missing_filters.any?
        aggregated_masks = aggregated_masks.select do |mask|
          missing_filters.all? { |missing_filter| matches_missing_filter?(mask, missing_filter) }
        end
      end
    end

    total_count = aggregated_masks.size

    decorated_masks = aggregated_masks.map do |mask|
      [mask, sort_value(mask, sort_column)]
    end
    non_nil, nils = decorated_masks.partition { |(_, value)| !value.nil? }
    non_nil.sort_by! { |(_, value)| value }
    non_nil.reverse! if sort_order == :desc
    sorted_masks = non_nil.map(&:first) + nils.map(&:first)

    start_index = (page - 1) * per_page
    paginated_masks = sorted_masks.slice(start_index, per_page) || []

    data_context = MasksDataContextualizer.call

    to_render = {
      masks: paginated_masks,
      total_count: total_count,
      page: page,
      per_page: per_page,
      context: data_context
    }

    respond_to do |format|
      format.json do
        render json: to_render.merge(messages: []), status: :ok
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    status = 200
    messages = []

    mask = if current_user&.admin
             Mask.with_admin_aggregations([params[:id]])[0]
           else
             Mask.with_privacy_aggregations([params[:id]])[0]
           end

    to_render = {
      mask: mask,
      context: MasksDataContextualizer.call
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
  end

  private

  def matches_missing_filter?(mask, filter_missing)
    case filter_missing
    when 'strap_type'
      value = mask['strap_type'] || mask[:strap_type]
      value.blank?
    when 'style'
      value = mask['style'] || mask[:style]
      value.blank?
    when 'perimeter'
      value = mask['perimeter_mm'] || mask[:perimeter_mm]
      value.nil? || value.to_f.zero?
    when 'filtration_factor'
      value = mask['avg_sealed_fit_factor'] || mask[:avg_sealed_fit_factor]
      value.nil? || value.to_f <= 0
    when 'breathability'
      value = mask['avg_breathability_pa'] || mask[:avg_breathability_pa]
      value.nil? || value.to_f <= 0
    else
      false
    end
  end

  def build_mask_events(mask, updates)
    events = []

    if updates.key?(:unique_internal_model_code) && updates[:unique_internal_model_code] != mask.unique_internal_model_code
      events << { event_type: 'unique_internal_model_code_updated',
                  data: { 'unique_internal_model_code' => updates[:unique_internal_model_code] } }
    end

    if updates.key?(:colors) && updates[:colors] != mask.colors
      events << { event_type: 'colors_updated', data: { 'action' => 'set', 'colors' => updates[:colors] } }
    end

    if updates.key?(:color) && updates[:color] != mask.color
      events << { event_type: 'color_changed', data: { 'color' => updates[:color] } }
    end

    if updates.key?(:notes) && updates[:notes] != mask.notes
      events << { event_type: 'notes_updated', data: { 'notes' => updates[:notes] } }
    end

    if updates.key?(:modifications) && updates[:modifications] != mask.modifications
      events << { event_type: 'modifications_updated', data: { 'modifications' => updates[:modifications] } }
    end

    if updates.key?(:mass_grams) && updates[:mass_grams] != mask.mass_grams
      events << { event_type: 'mass_updated', data: { 'mass_grams' => updates[:mass_grams] } }
    end

    if (updates.key?(:height_mm) && updates[:height_mm] != mask.height_mm) ||
       (updates.key?(:width_mm) && updates[:width_mm] != mask.width_mm) ||
       (updates.key?(:depth_mm) && updates[:depth_mm] != mask.depth_mm)
      events << {
        event_type: 'dimensions_updated',
        data: {
          'height_mm' => updates[:height_mm],
          'width_mm' => updates[:width_mm],
          'depth_mm' => updates[:depth_mm]
        }.compact
      }
    end

    if updates.key?(:perimeter_mm) && updates[:perimeter_mm] != mask.perimeter_mm
      events << { event_type: 'perimeter_updated', data: { 'perimeter_mm' => updates[:perimeter_mm] } }
    end

    if updates.key?(:filter_type) && updates[:filter_type] != mask.filter_type
      events << { event_type: 'filter_type_updated', data: { 'filter_type' => updates[:filter_type] } }
    end

    if updates.key?(:filtration_efficiencies) && updates[:filtration_efficiencies] != mask.filtration_efficiencies
      events << {
        event_type: 'filtration_efficiencies_updated',
        data: { 'action' => 'set', 'efficiencies' => updates[:filtration_efficiencies] }
      }
    end

    if updates.key?(:has_exhalation_valve) && updates[:has_exhalation_valve] != mask.has_exhalation_valve
      events << {
        event_type: 'exhalation_valve_updated',
        data: { 'has_exhalation_valve' => updates[:has_exhalation_valve] }
      }
    end

    if updates.key?(:breathability) && updates[:breathability] != mask.breathability
      events << { event_type: 'breathability_updated', data: { 'breathability' => updates[:breathability] } }
    end

    if (updates.key?(:initial_cost_us_dollars) && updates[:initial_cost_us_dollars] != mask.initial_cost_us_dollars) ||
       (updates.key?(:filter_change_cost_us_dollars) && updates[:filter_change_cost_us_dollars] != mask.filter_change_cost_us_dollars)
      cost_data = {}
      cost_data['initial_cost_us_dollars'] = updates[:initial_cost_us_dollars] if updates.key?(:initial_cost_us_dollars)
      if updates.key?(:filter_change_cost_us_dollars)
        cost_data['filter_change_cost_us_dollars'] =
          updates[:filter_change_cost_us_dollars]
      end
      events << { event_type: 'cost_updated', data: cost_data }
    end

    if updates.key?(:style) && updates[:style] != mask.style
      events << { event_type: 'style_updated', data: { 'style' => updates[:style] } }
    end

    if updates.key?(:image_urls) && updates[:image_urls] != mask.image_urls
      events << { event_type: 'image_urls_updated', data: { 'action' => 'set', 'urls' => updates[:image_urls] } }
    end

    if updates.key?(:where_to_buy_urls) && updates[:where_to_buy_urls] != mask.where_to_buy_urls
      events << { event_type: 'where_to_buy_urls_updated',
                  data: { 'action' => 'set', 'urls' => updates[:where_to_buy_urls] } }
    end

    if updates.key?(:strap_type) && updates[:strap_type] != mask.strap_type
      events << { event_type: 'strap_type_updated', data: { 'strap_type' => updates[:strap_type] } }
    end

    if updates.key?(:author_id) && updates[:author_id] != mask.author_id
      events << { event_type: 'author_updated', data: { 'author_id' => updates[:author_id] } }
    end

    if updates.key?(:brand_id) && updates[:brand_id] != mask.brand_id
      events << { event_type: 'brand_updated', data: { 'brand_id' => updates[:brand_id] } }
    end

    if updates.key?(:has_gasket) && updates[:has_gasket] != mask.has_gasket
      events << { event_type: 'gasket_updated', data: { 'has_gasket' => updates[:has_gasket] } }
    end

    if updates.key?(:sources) && updates[:sources] != mask.sources
      events << { event_type: 'sources_updated', data: { 'action' => 'set', 'sources' => updates[:sources] } }
    end

    if updates.key?(:age_range) && updates[:age_range] != mask.age_range
      events << { event_type: 'age_range_updated', data: { 'age_range' => updates[:age_range] } }
    end

    if updates.key?(:payable_datetimes) && updates[:payable_datetimes] != mask.payable_datetimes
      events << { event_type: 'payable_datetimes_updated',
                  data: { 'action' => 'set', 'datetimes' => updates[:payable_datetimes] } }
    end

    if updates.key?(:bulk_fit_tests_import_id) && updates[:bulk_fit_tests_import_id] != mask.bulk_fit_tests_import_id
      events << {
        event_type: 'bulk_import_updated',
        data: { 'bulk_fit_tests_import_id' => updates[:bulk_fit_tests_import_id] }
      }
    end

    if updates.key?(:duplicate_of) && updates[:duplicate_of] != mask.duplicate_of
      events << { event_type: 'duplicate_marked', data: { 'duplicate_of' => updates[:duplicate_of] } }
    end

    events
  end

  def update
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    end

    mask = Mask.find(params[:id])

    # TODO: admins should be able to update data no matter who owns it.
    if mask.author_id != current_user.id
      status = 401
      to_render = {}
      messages = ['Current user is not the author.']
    else
      updates = mask_data.to_h.deep_symbolize_keys
      events = build_mask_events(mask, updates)

      if events.empty?
        status = 204
        to_render = {}
        messages = []
      else
        begin
          MaskEvent.transaction do
            events.each do |event|
              MaskEvent.create!(
                mask: mask,
                user: current_user,
                event_type: event[:event_type],
                data: event[:data]
              )
            end

            mask.update!(MaskStatusBuilder.build_and_serialize(mask_id: mask.id))
          end

          status = 204
          to_render = {}
          messages = []
        rescue ActiveRecord::RecordInvalid => e
          status = 400 # bad request
          to_render = {}
          messages = Array(e.record&.errors&.full_messages || e.message)
        end
      end
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
  end

  def delete
    unless current_user
      status = 401
      to_render = {}
    end

    mask = Mask.find(params[:id])
    mask_with_aggregations = Mask.with_aggregations(mask.id)[0]

    if mask.author_id != current_user.id
      status = 401
      messages = ['Current user is not the Mask author.']
      to_render = {
        messages: messages
      }
    elsif mask_with_aggregations['fit_test_count'].positive?
      status = 401
      to_render = {
        messages: ['Cannot delete a mask that already has a Fit Test assigned to it.']
      }
    elsif mask.delete
      status = 200
      messages = []
      to_render = {
        messages: messages
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  public :update, :delete

  def mask_data
    params.require(:mask).permit(
      :author_id,
      :average_filtration_efficiency,
      :color,
      :unique_internal_model_code,
      :filter_type,
      :style,
      :strap_type,
      :mass_grams,
      :height_mm,
      :width_mm,
      :depth_mm,
      :perimeter_mm,
      :has_gasket,
      :has_exhalation_valve,
      :initial_cost_us_dollars,
      :filter_change_cost_us_dollars,
      :modifications,
      :notes,
      colors: [],
      sources: [],
      image_urls: [],
      where_to_buy_urls: [],
      filtration_efficiencies: %i[
        filtration_efficiency_percent
        filtration_efficiency_source
        filtration_efficiency_notes
      ],
      breathability: %i[
        breathability_pascals
        breathability_source
      ]
    )
  end

  def sort_value(mask, column)
    value = mask[column] || mask[column.to_s]

    return unless value

    if numeric?(value)
      value.to_f
    elsif value.is_a?(String)
      value.downcase
    else
      value
    end
  end

  def numeric?(value)
    return value.match?(/\A-?\d+(\.\d+)?\z/) if value.is_a?(String)

    value.is_a?(Numeric)
  end
end
