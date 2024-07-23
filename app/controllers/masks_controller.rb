class MasksController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    if unauthorized?
      status = 401
      message = "Unauthorized."
      mask = {}
    else

      mask = Mask.create(
        mask_data
      )

      if mask
        status = 201
        message = ""
      else
        status = 422
        message = "Mask creation failed."
        mask = {}
      end
    end

    to_render = {
      mask: mask,
      message: message
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
    message = ""

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      message = "Unauthorized."
      to_render = {}
    else
      to_render = {
        mask: JSON.parse(Mask.find(params[:id]).to_json)
      }
    end


    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def update
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      message = "Unauthorized."
      to_render = {}
    end

    mask = Mask.find(params[:id])


    # TODO: admins should be able to update data no matter who owns it.
    if !mask.author_ids.include?(current_user.id)
      status = 401
      to_render = {}
      message = 'Unauthorized.'
    elsif mask.update(mask_data)
      status = 204
      to_render = {}
      message = ""
    else
      status = 400 # bad request
      to_render = {}
      message = ""
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def mask_data
    params.require(:mask).permit(
      :unique_internal_model_code,
      :filter_type,
      :elastomeric,
      image_urls: [],
      author_ids: [],
      where_to_buy_urls: [],
      modifications: {},
    )
  end
end

