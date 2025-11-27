# frozen_string_literal: true

class BulkFitTestsImportsController < ApplicationController
  def create
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      bulk_import = {}
    else
      params_hash = bulk_import_params.merge(user: current_user)
      # Set default user_matching if not provided to avoid encryption issues
      params_hash[:user_matching] ||= '{}'

      bulk_import = BulkFitTestsImport.create(params_hash)

      if bulk_import.persisted?
        status = 201
        messages = []
      else
        status = 422
        messages = bulk_import.errors.full_messages
        bulk_import = {}
      end
    end

    to_render = {
      bulk_fit_tests_import: bulk_import,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def show
    bulk_import = BulkFitTestsImport.find(params[:id])

    if unauthorized?
      status = 401
      to_render = {}
    elsif !current_user.manages?(bulk_import.user)
      status = 422
      to_render = {}
    else
      status = 200
      messages = []
      to_render = {
        bulk_fit_tests_import: JSON.parse(bulk_import.to_json),
        messages: messages
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def update
    bulk_import = BulkFitTestsImport.find(params[:id])

    if unauthorized?
      status = 401
      to_render = {}
    elsif !current_user.manages?(bulk_import.user)
      status = 422
      to_render = {}
    else
      # Handle user creation if user_matching contains "__to_be_created__"
      user_matching_param = params.dig(:bulk_fit_tests_import, :user_matching)
      if user_matching_param.present?
        begin
          user_matching = JSON.parse(user_matching_param)
          updated_user_matching = create_users_for_matching(user_matching, bulk_import)

          # Update params with the modified user_matching
          params[:bulk_fit_tests_import][:user_matching] = updated_user_matching.to_json
        rescue JSON::ParserError => e
          status = 422
          to_render = {
            messages: ["Invalid user_matching format: #{e.message}"]
          }

          respond_to do |format|
            format.json do
              render json: to_render.to_json, status: status
            end
          end
          return
        rescue StandardError => e
          status = 422
          to_render = {
            messages: ["Error creating users: #{e.message}"]
          }

          respond_to do |format|
            format.json do
              render json: to_render.to_json, status: status
            end
          end
          return
        end
      end

      if bulk_import.update(bulk_import_params)
        status = 200
        messages = []
        to_render = {
          bulk_fit_tests_import: JSON.parse(bulk_import.to_json),
          messages: messages
        }
      else
        status = 422
        messages = bulk_import.errors.full_messages
        to_render = {
          messages: messages
        }
      end
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  private

  def bulk_import_params
    params.require(:bulk_fit_tests_import).permit(
      :source_name,
      :source_type,
      :import_data,
      :status,
      :user_matching,
      column_matching_mapping: {},
      mask_matching: {},
      user_seal_check_matching: {},
      fit_testing_matching: {}
    )
  end

  def create_users_for_matching(user_matching, _bulk_import)
    updated_user_matching = user_matching.dup
    created_users = {}

    user_matching.each do |key, value|
      next unless value == '__to_be_created__'

      # Parse key: "manager_email|||user_name"
      parts = key.split('|||')
      if parts.length != 2
        raise "Invalid user_matching key format: #{key}. Expected format: 'manager_email|||user_name'"
      end

      manager_email = parts[0].strip
      user_name = parts[1].strip

      # Find manager user by email
      manager_user = User.find_by(email: manager_email)
      raise "Manager not found with email: #{manager_email}" unless manager_user

      # Verify permission: admin can create for any manager, non-admin only for themselves
      unless current_user.admin || manager_user.id == current_user.id
        raise "You do not have permission to create users for manager: #{manager_email}"
      end

      # Parse user name into first_name and last_name
      # Split by space, first part is first_name, rest is last_name
      name_parts = user_name.split(/\s+/)
      first_name = name_parts[0] || ''
      last_name = name_parts.length > 1 ? name_parts[1..].join(' ') : ''

      # Create user, profile, and managed_user in a transaction
      ActiveRecord::Base.transaction do
        # Create user with a unique email
        new_user = User.new(
          email: "#{SecureRandom.uuid}@breathesafe-import.local",
          password: SecureRandom.uuid
        )
        new_user.skip_confirmation!
        new_user.save!

        # Create profile
        Profile.create!(
          user_id: new_user.id,
          first_name: first_name,
          last_name: last_name,
          measurement_system: 'imperial'
        )

        # Create managed_user
        ManagedUser.create!(
          manager_id: manager_user.id,
          managed_id: new_user.id
        )

        # Update user_matching with the created user's ID
        updated_user_matching[key] = new_user.id.to_s
        created_users[key] = new_user.id
      end
    end

    updated_user_matching
  end
end
