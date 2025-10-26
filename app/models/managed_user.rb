# frozen_string_literal: true

class ManagedUser < ApplicationRecord
  belongs_to :manager, class_name: 'User'
  belongs_to :managed, class_name: 'User'

  def self.for_manager_id(args)
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    managed_users = ManagedUser.includes(managed: :profile)
                               .where(manager_id: args[:manager_id])

    result = []

    managed_users.each do |mu|
      profile = mu.managed.profile
      latest_facial_measurement = FacialMeasurement.where(user_id: mu.managed_id)
                                                   .order(created_at: :desc)
                                                   .first

      # Build the result hash with decrypted values
      row = {
        # ManagedUser attributes
        'id' => mu.id,
        'manager_id' => mu.manager_id,
        'managed_id' => mu.managed_id,
        'created_at' => mu.created_at,
        'updated_at' => mu.updated_at,

        # Profile attributes (these will be automatically decrypted)
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
      }

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

    result
  end

  def self.for_manager_and_managed(args)
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    managed_user = ManagedUser.includes(managed: :profile)
                              .where(manager_id: args[:manager_id], managed_id: args[:managed_id])
                              .first

    return [] unless managed_user

    profile = managed_user.managed.profile
    latest_facial_measurement = FacialMeasurement.where(user_id: managed_user.managed_id)
                                                 .order(created_at: :desc)
                                                 .first

    # Build the result hash with decrypted values
    row = {
      # ManagedUser attributes
      'id' => managed_user.id,
      'manager_id' => managed_user.manager_id,
      'managed_id' => managed_user.managed_id,
      'created_at' => managed_user.created_at,
      'updated_at' => managed_user.updated_at,

      # Profile attributes (these will be automatically decrypted)
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
    }

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
