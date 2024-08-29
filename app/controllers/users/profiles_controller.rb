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
    if current_user.nil?
      status = 401
      messages = ["Unauthorized."]
    elsif !current_user.manages?(User.find(params['user_id']))
      status = 422
      message = ["User #{params['user_id']} is not managed by user #{current_user.id}"]
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
    if current_user.nil?
      status = 401
      message = ["Not signed in."]
    elsif !current_user.manages?(User.find(params['user_id']))
      status = 422
      message = ["User #{params['user_id']} is not managed by user #{current_user.id}"]
    else
      managed_users = ManagedUser.for_manager_and_managed( manager_id: current_user.id, managed_id: params['user_id'])

      profile = Profile.find_by(id: managed_users[0]['profile_id'])

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
      "year_of_birth",
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
