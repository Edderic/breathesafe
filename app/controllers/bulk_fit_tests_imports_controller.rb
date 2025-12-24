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

  def index
    if unauthorized?
      status = 401
      to_render = { bulk_fit_tests_imports: [], messages: ['Unauthorized.'] }
    else
      bulk_imports = BulkFitTestsImport.where(user: current_user).order(created_at: :desc)

      # Build response with fit test counts
      imports_data = bulk_imports.map do |import|
        fit_tests_added = import.fit_tests.count

        # Calculate fit_tests_to_add
        # For completed imports, use stored value if available, otherwise fall back to fit_tests_added
        # For pending imports, calculate from CSV data rows
        fit_tests_to_add = if import.status == 'completed'
                             # Check if fit_tests_to_add was stored in column_matching_mapping
                             stored_count = import.column_matching_mapping&.dig('fit_tests_to_add')
                             stored_count || fit_tests_added
                           else
                             # Parse CSV to count data rows (excluding header)
                             # This is an approximation - actual count depends on valid mask/user mappings
                             begin
                               import_data = import.import_data
                               if import_data.present?
                                 csv_lines = import_data.split("\n").reject(&:blank?)
                                 # Get header_row_index from column_matching_mapping if available
                                 header_row_index = import.column_matching_mapping&.dig('header_row_index')
                                 header_row_index = header_row_index.to_i if header_row_index
                                 header_row_index ||= 0
                                 # Count data rows (after header)
                                 data_rows = csv_lines.length > header_row_index ? csv_lines.length - header_row_index - 1 : 0
                                 [data_rows, 0].max
                               else
                                 0
                               end
                             rescue StandardError
                               0
                             end
                           end

        {
          id: import.id,
          source_name: import.source_name,
          status: import.status,
          fit_tests_to_add: fit_tests_to_add,
          fit_tests_added: fit_tests_added,
          created_at: import.created_at,
          updated_at: import.updated_at
        }
      end

      status = 200
      to_render = {
        bulk_fit_tests_imports: imports_data,
        messages: []
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def destroy
    bulk_import = BulkFitTestsImport.find(params[:id])

    if unauthorized?
      status = 401
      to_render = { messages: ['Unauthorized.'] }
    elsif !current_user.manages?(bulk_import.user)
      status = 422
      to_render = { messages: ['Unauthorized.'] }
    elsif bulk_import.destroy
      status = 200
      to_render = { messages: [] }
    else
      status = 422
      to_render = { messages: bulk_import.errors.full_messages }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def complete_import
    bulk_import = BulkFitTestsImport.find(params[:id])

    if unauthorized?
      status = 401
      to_render = { messages: ['Unauthorized.'] }
    elsif !current_user.manages?(bulk_import.user)
      status = 422
      to_render = { messages: ['Unauthorized.'] }
    elsif bulk_import.status == 'completed'
      status = 422
      to_render = { messages: ['Import has already been completed.'] }
    else
      begin
        fit_tests_data = params[:fit_tests_data] || []

        ActiveRecord::Base.transaction do
          fit_tests_data.each do |fit_test_data|
            # Extract data
            user_id = fit_test_data[:user_id] || fit_test_data['user_id']
            mask_id = fit_test_data[:mask_id] || fit_test_data['mask_id']
            testing_mode = fit_test_data[:testing_mode] || fit_test_data['testing_mode']
            facial_hair = fit_test_data[:facial_hair] || fit_test_data['facial_hair']
            user_seal_check = fit_test_data[:user_seal_check] || fit_test_data['user_seal_check']
            comfort = fit_test_data[:comfort] || fit_test_data['comfort']
            exercises = fit_test_data[:exercises] || fit_test_data['exercises'] || {}
            mask_modded = fit_test_data[:mask_modded] || fit_test_data['mask_modded'] || false

            # user_id is already the managed_user_id (user_id from ManagedUser)
            # No conversion needed - managed_user_id IS the user_id

            # Build results structure based on testing mode
            results = {}
            if %w[N95 N99].include?(testing_mode)
              # Quantitative fit test
              quantitative_exercises = []
              exercises.each do |key, value|
                next if value.blank?

                # Key is already the exercise name (e.g., "Bending over", "Talking")
                exercise_name = key.to_s
                quantitative_exercises << {
                  'name' => exercise_name,
                  'fit_factor' => value.to_s
                }
              end

              results['quantitative'] = {
                'testing_mode' => testing_mode,
                'exercises' => quantitative_exercises
              }
              # Also include qualitative defaults (null object pattern)
              results['qualitative'] ||= {
                'aerosol' => { 'solution' => 'Saccharin' },
                'exercises' => [
                  { 'name' => 'Normal breathing', 'result' => nil },
                  { 'name' => 'Deep breathing', 'result' => nil },
                  { 'name' => 'Turning head side to side', 'result' => nil },
                  { 'name' => 'Moving head up and down', 'result' => nil },
                  { 'name' => 'Talking', 'result' => nil },
                  { 'name' => 'Bending over', 'result' => nil },
                  { 'name' => 'Normal breathing', 'result' => nil }
                ],
                'procedure' => nil
              }
            elsif testing_mode == 'QLFT'
              # Qualitative fit test
              qualitative_exercises = []
              exercises.each do |key, value|
                next if value.blank?

                # Key is already the exercise name (e.g., "Bending over", "Talking")
                exercise_name = key.to_s
                qualitative_exercises << {
                  'name' => exercise_name,
                  'result' => value.to_s
                }
              end

              results['qualitative'] = {
                'exercises' => qualitative_exercises
              }
              # Also include quantitative defaults (null object pattern)
              results['quantitative'] ||= {
                'aerosol' => { 'solution' => 'Ambient', 'initial_count_per_cm3' => nil },
                'exercises' => [
                  { 'name' => 'Bending over', 'fit_factor' => nil },
                  { 'name' => 'Talking', 'fit_factor' => nil },
                  { 'name' => 'Turning head side to side', 'fit_factor' => nil },
                  { 'name' => 'Moving head up and down', 'fit_factor' => nil },
                  { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => nil }
                ],
                'procedure' => nil,
                'testing_mode' => 'N99'
              }
            end

            # Ensure results always has the proper structure (null object pattern)
            # This handles cases where testing_mode is missing or invalid
            if results.empty?
              results = {
                'qualitative' => {
                  'aerosol' => { 'solution' => 'Saccharin' },
                  'exercises' => [
                    { 'name' => 'Normal breathing', 'result' => nil },
                    { 'name' => 'Deep breathing', 'result' => nil },
                    { 'name' => 'Turning head side to side', 'result' => nil },
                    { 'name' => 'Moving head up and down', 'result' => nil },
                    { 'name' => 'Talking', 'result' => nil },
                    { 'name' => 'Bending over', 'result' => nil },
                    { 'name' => 'Normal breathing', 'result' => nil }
                  ],
                  'procedure' => nil
                },
                'quantitative' => {
                  'exercises' => [
                    { 'name' => 'Bending over', 'fit_factor' => nil },
                    { 'name' => 'Talking', 'fit_factor' => nil },
                    { 'name' => 'Turning head side to side', 'fit_factor' => nil },
                    { 'name' => 'Moving head up and down', 'fit_factor' => nil },
                    { 'name' => 'Normal breathing 1', 'fit_factor' => nil },
                    { 'name' => 'Normal breathing 2', 'fit_factor' => nil },
                    { 'name' => 'Grimace', 'fit_factor' => nil },
                    { 'name' => 'Deep breathing', 'fit_factor' => nil },
                    { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => nil }
                  ],
                  'testing_mode' => 'N95'
                }
              }
            end

            # Create fit test
            FitTest.create!(
              user_id: user_id,
              mask_id: mask_id,
              bulk_fit_tests_import_id: bulk_import.id,
              facial_hair: facial_hair,
              user_seal_check: user_seal_check,
              comfort: comfort,
              results: results,
              mask_modded: mask_modded
            )
          end

          # Mark import as completed and store fit_tests_to_add
          fit_tests_to_add = params[:fit_tests_to_add] || fit_tests_data.length
          bulk_import.update!(
            status: 'completed',
            column_matching_mapping: bulk_import.column_matching_mapping.merge('fit_tests_to_add' => fit_tests_to_add)
          )
        end

        status = 200
        to_render = {
          bulk_fit_tests_import: JSON.parse(bulk_import.reload.to_json),
          messages: []
        }
      rescue StandardError => e
        # Transaction will automatically rollback on exception
        status = 422
        to_render = {
          messages: ["Error importing fit tests: #{e.message}"]
        }
      end
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

      # Handle mask creation if mask_matching contains "__to_be_created__"
      mask_matching_param = params.dig(:bulk_fit_tests_import, :mask_matching)
      if mask_matching_param.present?
        begin
          updated_mask_matching = create_masks_for_matching(mask_matching_param, bulk_import)

          # Update params with the modified mask_matching
          params[:bulk_fit_tests_import][:mask_matching] = updated_mask_matching
        rescue StandardError => e
          status = 422
          to_render = {
            messages: ["Error creating masks: #{e.message}"]
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
      testing_mode_matching: {},
      qlft_values_matching: {},
      comfort_matching: {},
      fit_testing_matching: {},
      mask_modded_values_matching: {}
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

  def create_masks_for_matching(mask_matching, bulk_import)
    updated_mask_matching = mask_matching.dup

    mask_matching.each do |file_mask_name, value|
      next unless value == '__to_be_created__'

      # Create mask with file_mask_name as unique_internal_model_code
      # Author should be set to the manager (bulk_import.user)
      ActiveRecord::Base.transaction do
        new_mask = Mask.create!(
          unique_internal_model_code: file_mask_name,
          author_id: bulk_import.user_id,
          bulk_fit_tests_import_id: bulk_import.id
        )

        # Update mask_matching with the created mask's ID
        updated_mask_matching[file_mask_name] = new_mask.id.to_s
      end
    end

    updated_mask_matching
  end
end
