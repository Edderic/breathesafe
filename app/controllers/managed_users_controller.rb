# frozen_string_literal: true

# Controller for Managed Users
class ManagedUsersController < ApplicationController
  def index
    if current_user.nil?
      to_render = {
        managed_users: [],
        messages: ['Please log in.'],
        total_count: 0,
        page: 1,
        per_page: 25
      }
      status = 422
    else
      # Check if admin wants to see all users
      show_all_users = current_user.admin && params[:admin] == 'true'

      # Pagination params
      page = (params[:page] || 1).to_i
      per_page = (params[:per_page] || 25).to_i
      per_page = [per_page, 100].min # Cap at 100 per page

      # Sorting params
      sort_field = params[:sort]
      sort_order = params[:order]

      # Validate sort order
      sort_order = nil unless %w[asc desc].include?(sort_order)

      # Map frontend field names to database columns/calculations
      sort_column_map = {
        'name' => 'profiles.first_name',
        'manager_email' => 'users.email',
        'demog_percent_complete' => 'demog_percent_complete',
        'fm_percent_complete' => 'fm_percent_complete',
        'num_unique_masks_tested' => 'num_unique_masks_tested'
      }

      # Only apply sorting if both field and order are valid
      "#{sort_column_map[sort_field]} #{sort_order.upcase}" if sort_field && sort_order && sort_column_map[sort_field]

      if show_all_users
        # Admin viewing all users - get all managed users across all managers
        # Use for_manager_id_with_sort which can handle sorting
        managed_users = ManagedUser.for_all_users_paginated(
          page: page,
          per_page: per_page,
          sort_field: sort_field,
          sort_order: sort_order
        )

        total_count = ManagedUser.count

        to_render = {
          managed_users: managed_users,
          messages: [],
          total_count: total_count,
          page: page,
          per_page: per_page
        }
        status = 200
      else
        # Determine manager_id: use params if admin, otherwise use current_user.id
        manager_id = if current_user.admin && params[:manager_id].present?
                       params[:manager_id].to_i
                     else
                       current_user.id
                     end

        # Verify permission: admin can access any manager, non-admin only themselves
        if current_user.admin || manager_id == current_user.id
          total_count = ManagedUser.where(manager_id: manager_id).count

          # Get paginated and sorted managed users
          managed_users = ManagedUser.for_manager_id_paginated(
            manager_id: manager_id,
            page: page,
            per_page: per_page,
            sort_field: sort_field,
            sort_order: sort_order
          )

          to_render = {
            managed_users: managed_users,
            messages: [],
            total_count: total_count,
            page: page,
            per_page: per_page
          }

          status = 200
        else
          to_render = {
            managed_users: [],
            messages: ['Unauthorized.'],
            total_count: 0,
            page: page,
            per_page: per_page
          }
          status = 403
        end
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
      # Find the ManagedUser record by its ID
      managed_user = ManagedUser.find_by(id: params[:id])

      if managed_user.nil?
        messages = ['Managed user not found.']
        status = 404
      elsif managed_user.manager_id != current_user.id
        messages = ['Not authorized to delete this user.']
        status = 403
      else
        # Get the actual user ID (managed_id) to delete related records
        managed_id = managed_user.managed_id

        ActiveRecord::Base.transaction do
          user = User.find(managed_id)

          # Delete fit tests first
          facial_measurements = FacialMeasurement.where(user_id: managed_id)
          fit_tests = FitTest.where(facial_measurement_id: facial_measurements.map(&:id))
          fit_tests.destroy_all

          # Delete facial measurements
          facial_measurements.destroy_all

          # Delete profile
          profile = Profile.find_by(user_id: managed_id)
          profile&.destroy

          # Delete managed user relationships
          ManagedUser.where(managed_id: managed_id).destroy_all

          # Delete bulk fit test imports
          BulkFitTestsImport.where(user_id: managed_id).destroy_all

          # TODO: maybe not a good idea to destroy. We wanna know that the user
          # has consented, etc.
          user.destroy

          messages = ['User deleted successfully.']
          status = 200
        rescue ActiveRecord::RecordNotFound => e
          messages = ["User not found: #{e.message}"]
          status = 404
        rescue StandardError => e
          messages = ["Transaction to delete failed: #{e.message}"]
          status = 500
        end
      end
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
