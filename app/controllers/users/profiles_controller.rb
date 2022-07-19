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

  def show
    profile = current_user.profile

    to_render = {
      profile: profile,
      message: ""
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: 200
      end
    end
  end

  def create
    if unauthorized?
      status = 401
      message = "Unauthorized."
    else
      profile = Profile.create(user: current_user, measurement_system: measurement_system)

      if profile
        status = 201
        message = ""
      else
        status = 422
        message = "Profile creation failed."
      end
    end

    to_render = {
      profile: profile,
      message: message
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def update
    if unauthorized?
      status = 401
      message = "Unauthorized."
    else
      profile = current_user.profile
      status = 200

      if profile.update(profile_data)
        message = "Successfully updated."
      else
        message = "Did not update."
      end
    end

    to_render = {
      profile: profile,
      message: message
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def profile_data
    params.require(:profile).permit(
      "user_id",
      "measurement_system",
      "num_people_population",
      "num_positive_cases_last_seven_days",
      "uncounted_cases_multiplier",
      "mask_type"
    )
  end
end
