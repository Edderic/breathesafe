class Users::FacialMeasurementsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    for_user = User.find(params['user_id'])

    if unauthorized?
      status = 401
      messages = ["Unauthorized."]
      facial_measurement = {}

    elsif !current_user.manages?(
        for_user
      )
      status = 422
      message = ["Not managed by current user."]
    else
      # TODO: check that current_user is authorized to create a facial
      # measurement for given user_id

      facial_measurement = FacialMeasurement.create(
        facial_measurement_data
      )

      if facial_measurement.errors.full_messages.size > 0
        status = 422
        messages = facial_measurement.errors.full_messages
      else
        status = 201
        messages = []
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
    # TODO: check that the current user has access to data for particular user_id
    if !current_user
      status = 401
      messages = ["Unauthorized."]
      to_render = {
        messages: messages
      }

    elsif !current_user.manages?(
        User.find(params['user_id'])
      )
      status = 422
      message = ["Not managed by current user"]
    else
      to_render = {
        facial_measurements: JSON.parse(FacialMeasurement.where(user_id: params['user_id']).to_json),
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
      "nose_breadth",
      "nose_protrusion",
      "lip_width",
      "jaw_width",
      "face_depth",
      "face_length",
      "lower_face_length",
      "bitragion_menton_arc",
      "bitragion_subnasale_arc",
      "cheek_fullness",
      "head_circumference",
      "user_id"
    )
  end
end
