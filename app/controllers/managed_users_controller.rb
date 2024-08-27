class ManagedUsersController < ApplicationController
  def index
    if current_user.nil?
      to_render = {
        managed_users: [],
        messages: ['Please log in.']
      }
      status = 422
    else
      managed_users = ManagedUser.for_manager_id(manager_id: current_user.id)

      to_render = {
        managed_users: managed_users,
        messages: []
      }

      status = 200
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def create
    if current_user.nil?
      to_render = {
        managed_user: {},
        messages: ['Please log in.']
      }
      status = 422
    else
      ActiveRecord::Base.transaction do
        user = User.new(
          email: "#{SecureRandom.uuid}@fake.com",
          password: SecureRandom.uuid
        )

        user.skip_confirmation!
        user.save!

        profile = Profile.create!(
          user_id: user.id,
          first_name: "Edit",
          last_name: "Me",
          measurement_system: 'imperial'
        )

        ManagedUser.create!(
          manager_id: current_user.id,
          managed_id: user.id
        )

        to_render = {
          managed_user: ManagedUser.for_manager_and_managed(
            manager_id: current_user.id,
            managed_id: user.id
          ),
          messages: []
        }

        status = 201

      rescue ActiveRecord::StatementInvalid
        to_render = {
          managed_user: {},
          messages: ['Something went wrong']
        }

        status = 422

      end
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
    # create a user
    #
  end

  def show
    if current_user.nil?
      to_render = {
        managed_users: [],
        messages: ['Please log in.']
      }
      status = 422
    else
      managed_users = ManagedUser.for_manager_and_managed(
        manager_id: current_user.id,
        managed_id: params[:id]
      )

      to_render = {
        managed_users: managed_users,
        messages: []
      }

      status = 200
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end
end
