# frozen_string_literal: true

# Controller for Managed Users
class ManagedUsersController < ApplicationController
  def index
    if current_user.nil?
      to_render = {
        managed_users: [],
        messages: ['Please log in.']
      }
      status = 422
    else
      # Determine manager_id: use params if admin, otherwise use current_user.id
      manager_id = if current_user.admin && params[:manager_id].present?
                     params[:manager_id].to_i
                   else
                     current_user.id
                   end

      # Verify permission: admin can access any manager, non-admin only themselves
      unless current_user.admin || manager_id == current_user.id
        to_render = {
          managed_users: [],
          messages: ['Unauthorized.']
        }
        status = 403
      else
        managed_users = ManagedUser.for_manager_id(manager_id: manager_id)

        to_render = {
          managed_users: managed_users,
          messages: []
        }

        status = 200
      end
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

        Profile.create!(
          user_id: user.id,
          first_name: 'Edit',
          last_name: 'Me',
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
          )[0],
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

  def delete
    messages = []

    if current_user.nil?

      messages = ['Please log in.']
      status = 422
    else
      ManagedUser.for_manager_and_managed(
        manager_id: current_user.id,
        managed_id: params[:id]
      )

      ActiveRecord::Base.transaction do
        facial_measurements = FacialMeasurement.where(user_id: params[:id])
        fit_tests = FitTest.where(facial_measurement_id: facial_measurements.map(&:id))
        fit_tests.destroy_all

        facial_measurements.destroy_all

        profile = Profile.find_by(user_id: params[:id])
        profile.destroy

        ManagedUser.where(managed_id: params[:id]).destroy_all

        User.find(params[:id]).destroy
      rescue ActiveRecord::StatementInvalid
        messages = ['Transaction to delete failed.']
      end

      status = 200
    end

    to_render = {
      managed_users: [],
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def facial_measurements
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      facial_measurements = []
    else
      facial_measurements = FacialMeasurementOutliersService.call(manager_id: current_user.id)
      messages = []
      status = 200
    end

    to_render = {
      facial_measurements: facial_measurements,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end
end
