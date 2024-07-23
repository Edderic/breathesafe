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
        masks: JSON.parse(Mask.where(user_id: current_user.id).to_json)
      }
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

