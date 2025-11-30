# frozen_string_literal: true

class ManagedUser < ApplicationRecord
  belongs_to :manager, class_name: 'User'
  belongs_to :managed, class_name: 'User'

  def self.for_manager_id(args)
    start_time = Time.current
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    query_start = Time.current
    managed_users = ManagedUser.includes(managed: :profile)
                               .where(manager_id: args[:manager_id])
    Rails.logger.debug "ManagedUser.for_manager_id: Initial query took: #{(Time.current - query_start) * 1000}ms, found #{managed_users.length} managed users"

    result = []

    # Collect all managed_ids to preload facial measurements
    collect_start = Time.current
    managed_ids = managed_users.map(&:managed_id).compact.uniq
    Rails.logger.debug "ManagedUser.for_manager_id: Collecting managed_ids took: #{(Time.current - collect_start) * 1000}ms, found #{managed_ids.length} unique IDs"

    # Preload latest facial measurements for all managed users efficiently
    # Use PostgreSQL's DISTINCT ON to get only the latest measurement per user in a single query
    facial_measurement_start = Time.current
    if managed_ids.any?
      # Use raw SQL with DISTINCT ON for efficiency (PostgreSQL-specific)
      # This gets the latest facial measurement per user in a single query
      # Use sanitize_sql_array for safe parameter binding
      sql = ActiveRecord::Base.sanitize_sql_array([
                                                    <<-SQL.squish, managed_ids
          SELECT DISTINCT ON (user_id) *
          FROM facial_measurements
          WHERE user_id IN (?)
          ORDER BY user_id, created_at DESC
                                                    SQL
                                                  ])
      latest_facial_measurements = FacialMeasurement.find_by_sql(sql).index_by(&:user_id)
      Rails.logger.debug "ManagedUser.for_manager_id: Facial measurement query took: #{(Time.current - facial_measurement_start) * 1000}ms, loaded #{latest_facial_measurements.length} measurements"
    else
      latest_facial_measurements = {}
      Rails.logger.debug 'ManagedUser.for_manager_id: No managed_ids, skipped facial measurement query'
    end

    # Preload unique mask counts for all managed users efficiently
    mask_count_start = Time.current
    unique_mask_counts = if managed_ids.any?
                           # Count unique masks tested per user
                           FitTest.where(user_id: managed_ids)
                                  .joins(:mask)
                                  .where('masks.duplicate_of IS NULL')
                                  .group(:user_id)
                                  .count('DISTINCT fit_tests.mask_id')
                         else
                           {}
                         end
    Rails.logger.debug "ManagedUser.for_manager_id: Unique mask count query took: #{(Time.current - mask_count_start) * 1000}ms, found #{unique_mask_counts.length} users"

    loop_start = Time.current
    managed_users.each do |mu|
      profile = mu.managed.profile
      latest_facial_measurement = latest_facial_measurements[mu.managed_id]

      # Calculate demographics completion percentage
      demog_percent_complete = 0
      if profile
        demog_fields = [
          profile.race_ethnicity,
          profile.gender_and_sex,
          profile.year_of_birth,
          profile.demographics
        ]
        completed_demog_fields = demog_fields.count(&:present?)
        demog_percent_complete = (completed_demog_fields.to_f / demog_fields.length * 100).round
      end

      # Calculate facial measurements completion percentage
      fm_percent_complete = 0
      if latest_facial_measurement
        # Use the percent_complete method from FacialMeasurement
        # This calculates based on aggregated ARKit measurements (nose, strap, top_cheek, mid_cheek, chin)
        fm_percent_complete = latest_facial_measurement.percent_complete.to_f
      end

      # Get unique masks tested count
      num_unique_masks_tested = unique_mask_counts[mu.managed_id] || 0

      # Build the result hash with decrypted values
      row = {
        # ManagedUser attributes
        'id' => mu.id,
        'manager_id' => mu.manager_id,
        'managed_id' => mu.managed_id,
        'created_at' => mu.created_at,
        'updated_at' => mu.updated_at,
        # Calculated completion percentages
        'demog_percent_complete' => demog_percent_complete,
        'fm_percent_complete' => fm_percent_complete,
        'num_unique_masks_tested' => num_unique_masks_tested
      }

      # Profile attributes (these will be automatically decrypted)
      # Handle case where profile might not exist
      if profile
        row.merge!({
                     'user_id' => profile.user_id,
                     'measurement_system' => profile.measurement_system,
                     'num_positive_cases_last_seven_days' => profile.num_positive_cases_last_seven_days,
                     'num_people_population' => profile.num_people_population,
                     'uncounted_cases_multiplier' => profile.uncounted_cases_multiplier,
                     'mask_type' => profile.mask_type,
                     'event_display_risk_time' => profile.event_display_risk_time,
                     'first_name' => profile.first_name,  # This will be decrypted
                     'last_name' => profile.last_name,    # This will be decrypted
                     'height_meters' => profile.height_meters,
                     'stride_length_meters' => profile.stride_length_meters,
                     'socials' => profile.socials,
                     'external_api_token' => profile.external_api_token,
                     'can_post_via_external_api' => profile.can_post_via_external_api,
                     'demographics' => profile.demographics,
                     'race_ethnicity' => profile.race_ethnicity,
                     'gender_and_sex' => profile.gender_and_sex,
                     'other_gender' => profile.other_gender,
                     'year_of_birth' => profile.year_of_birth,
                     'study_start_datetime' => profile.study_start_datetime,
                     'study_goal_end_datetime' => profile.study_goal_end_datetime,
                     'profile_id' => profile.id
                   })
      else
        # Set default values when profile doesn't exist
        row.merge!({
                     'user_id' => mu.managed_id,
                     'measurement_system' => nil,
                     'num_positive_cases_last_seven_days' => nil,
                     'num_people_population' => nil,
                     'uncounted_cases_multiplier' => nil,
                     'mask_type' => nil,
                     'event_display_risk_time' => nil,
                     'first_name' => nil,
                     'last_name' => nil,
                     'height_meters' => nil,
                     'stride_length_meters' => nil,
                     'socials' => nil,
                     'external_api_token' => nil,
                     'can_post_via_external_api' => nil,
                     'demographics' => nil,
                     'race_ethnicity' => nil,
                     'gender_and_sex' => nil,
                     'other_gender' => nil,
                     'year_of_birth' => nil,
                     'study_start_datetime' => nil,
                     'study_goal_end_datetime' => nil,
                     'profile_id' => nil
                   })
      end

      # Add facial measurement data if available
      if latest_facial_measurement
        row.merge!({
                     'facial_measurement_id' => latest_facial_measurement.id,
                     'source' => latest_facial_measurement.source,
                     'face_width' => latest_facial_measurement.face_width,
                     'jaw_width' => latest_facial_measurement.jaw_width,
                     'face_depth' => latest_facial_measurement.face_depth,
                     'face_length' => latest_facial_measurement.face_length,
                     'lower_face_length' => latest_facial_measurement.lower_face_length,
                     'bitragion_menton_arc' => latest_facial_measurement.bitragion_menton_arc,
                     'bitragion_subnasale_arc' => latest_facial_measurement.bitragion_subnasale_arc,
                     'cheek_fullness' => latest_facial_measurement.cheek_fullness,
                     'nasal_root_breadth' => latest_facial_measurement.nasal_root_breadth,
                     'nose_protrusion' => latest_facial_measurement.nose_protrusion,
                     'nose_bridge_height' => latest_facial_measurement.nose_bridge_height,
                     'lip_width' => latest_facial_measurement.lip_width,
                     'head_circumference' => latest_facial_measurement.head_circumference,
                     'nose_breadth' => latest_facial_measurement.nose_breadth,
                     'arkit' => latest_facial_measurement.arkit
                   })
      end

      result << row
    end
    Rails.logger.debug "ManagedUser.for_manager_id: Main loop took: #{(Time.current - loop_start) * 1000}ms, processed #{result.length} rows"
    Rails.logger.debug "ManagedUser.for_manager_id total time: #{(Time.current - start_time) * 1000}ms"

    result
  end

  def self.for_manager_and_managed(args)
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    managed_user = ManagedUser.includes(managed: :profile)
                              .where(manager_id: args[:manager_id], managed_id: args[:managed_id])
                              .first

    return [] unless managed_user

    profile = managed_user.managed.profile
    # For single user, we can still optimize by using a more efficient query
    latest_facial_measurement = FacialMeasurement.where(user_id: managed_user.managed_id)
                                                 .order(created_at: :desc)
                                                 .limit(1)
                                                 .first

    # Build the result hash with decrypted values
    row = {
      # ManagedUser attributes
      'id' => managed_user.id,
      'manager_id' => managed_user.manager_id,
      'managed_id' => managed_user.managed_id,
      'created_at' => managed_user.created_at,
      'updated_at' => managed_user.updated_at
    }

    # Profile attributes (these will be automatically decrypted)
    # Handle case where profile might not exist
    if profile
      row.merge!({
                   'user_id' => profile.user_id,
                   'measurement_system' => profile.measurement_system,
                   'num_positive_cases_last_seven_days' => profile.num_positive_cases_last_seven_days,
                   'num_people_population' => profile.num_people_population,
                   'uncounted_cases_multiplier' => profile.uncounted_cases_multiplier,
                   'mask_type' => profile.mask_type,
                   'event_display_risk_time' => profile.event_display_risk_time,
                   'first_name' => profile.first_name,  # This will be decrypted
                   'last_name' => profile.last_name,    # This will be decrypted
                   'height_meters' => profile.height_meters,
                   'stride_length_meters' => profile.stride_length_meters,
                   'socials' => profile.socials,
                   'external_api_token' => profile.external_api_token,
                   'can_post_via_external_api' => profile.can_post_via_external_api,
                   'demographics' => profile.demographics,
                   'race_ethnicity' => profile.race_ethnicity,
                   'gender_and_sex' => profile.gender_and_sex,
                   'other_gender' => profile.other_gender,
                   'year_of_birth' => profile.year_of_birth,
                   'study_start_datetime' => profile.study_start_datetime,
                   'study_goal_end_datetime' => profile.study_goal_end_datetime,
                   'profile_id' => profile.id
                 })
    else
      # Set default values when profile doesn't exist
      row.merge!({
                   'user_id' => managed_user.managed_id,
                   'measurement_system' => nil,
                   'num_positive_cases_last_seven_days' => nil,
                   'num_people_population' => nil,
                   'uncounted_cases_multiplier' => nil,
                   'mask_type' => nil,
                   'event_display_risk_time' => nil,
                   'first_name' => nil,
                   'last_name' => nil,
                   'height_meters' => nil,
                   'stride_length_meters' => nil,
                   'socials' => nil,
                   'external_api_token' => nil,
                   'can_post_via_external_api' => nil,
                   'demographics' => nil,
                   'race_ethnicity' => nil,
                   'gender_and_sex' => nil,
                   'other_gender' => nil,
                   'year_of_birth' => nil,
                   'study_start_datetime' => nil,
                   'study_goal_end_datetime' => nil,
                   'profile_id' => nil
                 })
    end

    # Add facial measurement data if available
    if latest_facial_measurement
      row.merge!({
                   'facial_measurement_id' => latest_facial_measurement.id,
                   'source' => latest_facial_measurement.source,
                   'face_width' => latest_facial_measurement.face_width,
                   'jaw_width' => latest_facial_measurement.jaw_width,
                   'face_depth' => latest_facial_measurement.face_depth,
                   'face_length' => latest_facial_measurement.face_length,
                   'lower_face_length' => latest_facial_measurement.lower_face_length,
                   'bitragion_menton_arc' => latest_facial_measurement.bitragion_menton_arc,
                   'bitragion_subnasale_arc' => latest_facial_measurement.bitragion_subnasale_arc,
                   'cheek_fullness' => latest_facial_measurement.cheek_fullness,
                   'nasal_root_breadth' => latest_facial_measurement.nasal_root_breadth,
                   'nose_protrusion' => latest_facial_measurement.nose_protrusion,
                   'nose_bridge_height' => latest_facial_measurement.nose_bridge_height,
                   'lip_width' => latest_facial_measurement.lip_width,
                   'head_circumference' => latest_facial_measurement.head_circumference,
                   'nose_breadth' => latest_facial_measurement.nose_breadth,
                   'arkit' => latest_facial_measurement.arkit
                 })

      # Calculate missing ratio if needed
      # Note: This is a simplified version - you may need to implement the full missing_ratio_sql logic
      row['missing_ratio'] = 0.0 # Placeholder - implement actual calculation if needed
    end

    [row]
  end
end
