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
    # Extract pagination and search parameters
    page = params[:page]&.to_i || 1
    per_page = params[:per_page]&.to_i || 6
    search = params[:search]

    # Get base query
    masks_query = Mask.all

    # Apply search filter if provided
    masks_query = masks_query.where('unique_internal_model_code ILIKE ?', "%#{search}%") if search.present?

    # Get total count before pagination
    total_count = masks_query.count

    # Apply pagination
    offset = (page - 1) * per_page
    mask_ids = masks_query.order(:id).offset(offset).limit(per_page).pluck(:id)

    # Get masks with aggregations
    masks = if current_user&.admin
              Mask.with_admin_aggregations(mask_ids)
            else
              Mask.with_privacy_aggregations(mask_ids)
            end

    to_render = {
      masks: masks,
      total_count: total_count,
      page: page,
      per_page: per_page
    }
    messages = []
    status = 200

    respond_to do |format|
      format.json do
        render json: to_render.merge(messages: messages), status: status
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
