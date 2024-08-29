class MasksController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    if unauthorized?
      status = 401
      messages = ["Unauthorized."]
      mask = {}
    else
      hashed_mask_data = mask_data.to_hash
      hashed_mask_data[:author_id] = current_user.id
      mask = Mask.create(hashed_mask_data)

      if mask.errors.full_messages.size == 0
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
    to_render = {
      masks: JSON.parse(
        Mask.all.to_json
      )
    }
    messages = []

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      messages = ["Unauthorized."]
      to_render = {}
    else
      to_render = {
        mask: JSON.parse(Mask.find(params[:id]).to_json)
      }
    end


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
      messages = ["Unauthorized."]
      to_render = {}
    end

    mask = Mask.find(params[:id])


    # TODO: admins should be able to update data no matter who owns it.
    if mask.author_id != current_user.id
      status = 401
      to_render = {}
      messages = ['Unauthorized.']
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
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      messages = ["Unauthorized."]
      to_render = {}
    end

    mask = Mask.find(params[:id])


    # TODO: admins should be able to update data no matter who owns it.
    if mask.author_id != current_user.id
      status = 401
      to_render = {}
      messages = ['Unauthorized.']
    elsif mask.delete
      status = 200
      to_render = {}
      messages = []
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
  end

  def mask_data
    params.require(:mask).permit(
      :author_id,
      :unique_internal_model_code,
      :filter_type,
      :style,
      :strap_type,
      :mass_grams,
      :height_mm,
      :width_mm,
      :depth_mm,
      :has_gasket,
      :has_exhalation_valve,
      :initial_cost_us_dollars,
      :filter_change_cost_us_dollars,
      :notes,
      sources: [],
      image_urls: [],
      where_to_buy_urls: [],
      modifications: {},
      filtration_efficiencies: [
        :filtration_efficiency_percent,
        :filtration_efficiency_source,
        :filtration_efficiency_notes
      ],
      breathability: [
        :breathability_pascals,
        :breathability_source
      ]
    )
  end
end

