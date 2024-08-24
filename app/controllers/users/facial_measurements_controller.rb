class Users::FacialMeasurementsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    if unauthorized?
      status = 401
      messages = ["Unauthorized."]
      facial_measurement = {}
    else

      facial_measurement = FacialMeasurement.create(
        facial_measurement_data
      )

      if facial_measurement.errors.full_messages
        status = 422
        messages = facial_measurement.errors.full_messages
      else
        status = 201
        messages = []
        facial_measurement = {}
      end
    end

    to_render = {
      facial_measurement: facial_measurement,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      messages = ["Unauthorized."]
      to_render = {
        messages: messages
      }
    else
      to_render = {
        facial_measurements: JSON.parse(FacialMeasurement.where(user_id: current_user.id).to_json)
        messages: []
      }
    end


    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def facial_measurement_data
    params.require(:facial_measurement).permit(
      "source",
      "face_width",
      "nose_bridge_height",
      "nasal_root_breadth",
      "nose_protrusion",
      "lip_width",
      "jaw_width",
      "face_depth",
      "face_length",
      "lower_face_length",
      "bitragion_menton_arc",
      "bitragion_subnasale_arc",
      "cheek_fullness",
      "user_id"
    )
  end
end
