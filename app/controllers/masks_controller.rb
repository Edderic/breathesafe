# frozen_string_literal: true

# Controller with CRUD operations for Masks
class MasksController < ApplicationController
  skip_before_action :verify_authenticity_token

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
    allowed_sort_columns = %w[
      unique_fit_testers_count
      fit_test_count
      perimeter_mm
      unique_internal_model_code
    ]

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
    sort_by = allowed_sort_columns.include?(permitted[:sort_by]) ? permitted[:sort_by] : 'id'
    sort_order = permitted[:sort_order] == 'descending' ? :desc : :asc

    masks_query = Mask.all
    masks_query = masks_query.where('unique_internal_model_code ILIKE ?', "%#{search}%") if search
    masks_query = masks_query.where(style: filter_style) if filter_style && filter_style != 'none'
    masks_query = masks_query.where(strap_type: filter_strap_type) if filter_strap_type && filter_strap_type != 'none'
    masks_query = masks_query.where('colors @> ?', [filter_color].to_json) if filter_color && filter_color != 'none'

    total_count = masks_query.count
    offset = (page - 1) * per_page
    ordered_scope = sort_by == 'id' ? masks_query.order(:id) : masks_query.order(sort_by => sort_order)
    mask_ids = ordered_scope.offset(offset).limit(per_page).pluck(:id)

    masks = if current_user&.admin
              Mask.with_admin_aggregations(mask_ids)
            else
              Mask.with_privacy_aggregations(mask_ids)
            end

    masks_by_id = masks.index_by { |mask| mask['id'] || mask[:id] }
    ordered_masks = mask_ids.filter_map { |mask_id| masks_by_id[mask_id] }

    to_render = {
      masks: ordered_masks,
      total_count: total_count,
      page: page,
      per_page: per_page
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
end
