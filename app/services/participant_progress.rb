class ParticipantProgress
  # tracks the progress of a participant in the Mask Recommender Based on
  # Facial Features
  #
  def self.facial_measurements_present_sql
    FacialMeasurement::COLUMNS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != 0 THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end#

  def self.string_demographics_present_sql
    Profile::STRING_DEMOG_FIELDS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != '' THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end#

  def self.numeric_demographics_present_sql
    Profile::NUM_DEMOG_FIELDS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != 0 THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end#

  def self.demographics_present_sql
    (string_demographics_present_sql + ',' + numeric_demographics_present_sql)
  end#

  def self.demographics_present_counts
    (Profile::STRING_DEMOG_FIELDS + Profile::NUM_DEMOG_FIELDS).map do |c|
      "#{c}_present"
    end.join('+') + " AS demog_present_counts"
  end#


  def self.facial_measurements_present_counts
    FacialMeasurement::COLUMNS.map do |c|
      "#{c}_present"
    end.join('+') + " AS fm_present_counts"
  end#


  def self.call(manager_id:)
    ActiveRecord::Base.connection.exec_query(
      <<-SQL
        WITH managed_by_manager AS (
          SELECT * FROM managed_users
          WHERE manager_id = '#{manager_id}'
        ), latest_facial_measurement_created_at AS (
          SELECT user_id, MAX(created_at) AS created_at
          FROM facial_measurements fm
          GROUP BY 1
        ), latest_facial_measurement_with_present AS (
          SELECT fm.*,
          #{self.facial_measurements_present_sql}
          FROM facial_measurements fm
          INNER JOIN latest_facial_measurement_created_at lfm
          ON fm.user_id = lfm.user_id
          AND fm.created_at = lfm.created_at
        ), latest_facial_measurement_with_present_counts AS (
          SELECT id,
           created_at,
           updated_at,
           #{self.facial_measurements_present_counts},
           user_id
          FROM latest_facial_measurement_with_present
        ), profile_with_demog_fields_present AS (
          SELECT *, #{demographics_present_sql}
          FROM profiles

        ), profile_with_demog_fields_present_count AS (
          SELECT *,
            #{demographics_present_counts}
          FROM profile_with_demog_fields_present
        ), targeted_masks AS (
          SELECT * FROM masks
          WHERE json_array_length(payable_datetimes) > 0
        ), targeted_fit_tests AS (
          SELECT targeted_masks.id,
          fit_tests.user_id

          FROM targeted_masks
          INNER JOIN fit_tests
          ON targeted_masks.id = fit_tests.mask_id
        ), targeted_mask_counts AS (
          SELECT user_id, id, COUNT(*) AS num_fit_tests_per_mask
          FROM targeted_fit_tests
          GROUP BY 1, 2
        ), total_unique_masks_fit_tested AS (
          SELECT user_id, COUNT(id) AS num_targeted_unique_masks_fit_tested
          FROM targeted_mask_counts
          GROUP BY 1
        ), managers_who_are_study_participants AS (
          SELECT users.* FROM users
          INNER JOIN profiles
          ON profiles.user_id = users.id
          WHERE profiles.study_start_datetime IS NOT NULL
        ), targeted_masks_count AS (
          SELECT COUNT(*) AS num_targeted_masks
          FROM targeted_masks

        )





        SELECT
        p.first_name,
        p.last_name,
        num_targeted_masks,
        total_unique_masks_fit_tested.num_targeted_unique_masks_fit_tested,
        ROUND((num_targeted_unique_masks_fit_tested::float / num_targeted_masks * 100)::numeric, 2) AS fit_testing_percent_complete,
        CASE WHEN demog_present_counts IS NULL THEN 0 ELSE demog_present_counts END AS demog_present_counts,
        CASE WHEN fm_present_counts IS NULL THEN 0 ELSE fm_present_counts END AS fm_present_counts,
        ROUND(CAST(CASE WHEN fm_present_counts IS NULL THEN 0 ELSE fm_present_counts END::float / #{FacialMeasurement::COLUMNS.size} * 100 AS NUMERIC), 2) AS fm_percent_complete,
        ROUND(CAST(CASE WHEN demog_present_counts IS NULL THEN 0 ELSE demog_present_counts END::float / #{Profile::STRING_DEMOG_FIELDS.size + Profile::NUM_DEMOG_FIELDS.size} * 100 AS NUMERIC), 2) AS demog_percent_complete,
        managed_users.*, fm.created_at, fm.updated_at

        FROM managers_who_are_study_participants
        LEFT JOIN managed_users
          ON managed_users.manager_id = managers_who_are_study_participants.id
        LEFT JOIN profile_with_demog_fields_present_count p
          ON managed_users.managed_id = p.user_id
        LEFT JOIN latest_facial_measurement_with_present_counts fm
          ON fm.user_id = managed_users.managed_id
        LEFT JOIN total_unique_masks_fit_tested
          ON total_unique_masks_fit_tested.user_id = managed_users.managed_id
        CROSS JOIN targeted_masks_count


      SQL
    )
  end

end
