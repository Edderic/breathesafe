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
      :filter_strap_type
    )

    page = permitted[:page].to_i.positive? ? permitted[:page].to_i : 1
    per_page = permitted[:per_page].to_i.positive? ? permitted[:per_page].to_i : 12
    search = permitted[:search].presence
    filter_color = permitted[:filter_color].presence
    filter_style = permitted[:filter_style].presence
    filter_strap_type = permitted[:filter_strap_type].presence
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
    total_count = mask_ids.size

    aggregated_masks = if current_user&.admin
                         Mask.with_admin_aggregations(mask_ids)
                       else
                         Mask.with_privacy_aggregations(mask_ids)
                       end
    mask_id_lookup = mask_ids.index_with { |_id| true }
    aggregated_masks.select! do |mask|
      mask_id_lookup[mask['id']] || mask_id_lookup[mask[:id]]
    end

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
      mask: mask
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
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
    elsif mask.update(mask_data)
      status = 204
      to_render = {}
      messages = []
    else
      status = 400 # bad request
      to_render = {}
      messages = []
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

  private

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
