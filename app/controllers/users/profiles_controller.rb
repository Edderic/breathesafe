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
      messages = ["Unauthorized."]
    else
      measurement_system = "imperial"
      profile = Profile.create(user: current_user, measurement_system: measurement_system)

      if profile.errors.full_messages.size > 0
        status = 422
        messages = profile.errors.full_messages
      else
        status = 201
        messages = []
      end
    end

    to_render = {
      profile: profile,
      messages: messages
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
        messages = []
      else
        messages = ["Did not update."]
        status = 422
      end
    end

    to_render = {
      profile: profile,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def profile_data
    params.require(:profile).permit(
      "race_ethnicity",
      "gender_and_sex",
      "other_gender",
      "height_meters",
      "stride_length_meters",
      "first_name",
      "last_name",
      "measurement_system",
      "user_id",
      "socials": [:mastodon, :twitter, :facebook]
    )
  end
end
