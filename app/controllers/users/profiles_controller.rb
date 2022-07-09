class Users::ProfilesController < ApplicationController
  skip_before_action :verify_authenticity_token

  def index
    respond_to do |format|
      format.json do
        render json: {
          'carbonDioxideMonitors': current_user.carbon_dioxide_monitors
        }.to_json
      end
    end
  end

  def create_or_update
    if profile_data['measurement_system'].blank?
      measurement_system = 'imperial'
    else
      measurement_system = profile_data['measurement_system']
    end

    if unauthorized?
      status = 401
      message = "Unauthorized."
    else
      profile = current_user.profile
      status = 200

      if profile
        if profile.measurement_system == profile_data['measurement_system']
          message = ""
        elsif profile.update(user: current_user, measurement_system: measurement_system)
          message = "Successfully updated measurement system to #{measurement_system}."
        else
          message = ""
        end
      else
        profile = Profile.create(user: current_user, measurement_system: measurement_system)

        unless profile
          message = "Failed to create profile."
        end
      end
    end

    to_render = {
      systemOfMeasurement: measurement_system,
      message: message
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def profile_data
    params.require(:profile).permit("measurement_system")
  end
end
