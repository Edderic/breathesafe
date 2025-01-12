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
    user = User.find(manager_id)
    if user.admin?
      where = ''
    else
      where = "WHERE managed_users.manager_id = #{manager_id}"
    end

    JSON.parse(
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
          LEFT JOIN profiles
          ON profiles.user_id = users.id
        ), targeted_masks_count AS (
          SELECT COUNT(*) AS num_targeted_masks
          FROM targeted_masks

        ),
        latest_shipping_status_refresh_datetimes AS (
          SELECT uuid, MAX(refresh_datetime) as refresh_datetime
          FROM shipping_statuses
          GROUP BY 1
        ), latest_shipping_statuses AS (
          SELECT ss.* FROM shipping_statuses ss
          INNER JOIN latest_shipping_status_refresh_datetimes lssrd
          ON lssrd.uuid = ss.uuid
          AND lssrd.refresh_datetime = ss.refresh_datetime
        ),
        latest_shipping_status_join_refresh AS (
            SELECT shipping_uuid, shippable_uuid, MAX(refresh_datetime) AS refresh_datetime
            FROM shipping_status_joins
            GROUP BY 1,2
        ), latest_shipping_status_joins AS (
            SELECT ssj.* FROM shipping_status_joins ssj
            INNER JOIN latest_shipping_status_join_refresh
            ON ssj.shipping_uuid = latest_shipping_status_join_refresh.shipping_uuid
                AND ssj.shippable_uuid = latest_shipping_status_join_refresh.shippable_uuid
                AND ssj.refresh_datetime = latest_shipping_status_join_refresh.refresh_datetime
        ), latest_sent_masks AS (
            SELECT us.uuid as us_uuid,
                mask_uuid
            FROM user_statuses us
            LEFT JOIN shipping_statuses ss
            ON ss.to_user_uuid = us.uuid
            LEFT JOIN latest_shipping_status_joins lssj
            ON lssj.shipping_uuid = ss.uuid
            LEFT JOIN mask_kit_statuses mks
            ON mks.uuid = lssj.shippable_uuid
            WHERE lssj.shippable_type = 'MaskKit'
        ), latest_sent_masks_counts AS (
            SELECT us_uuid, COUNT(mask_uuid) AS num_targeted_masks
            FROM latest_sent_masks
            GROUP BY 1
        )


        SELECT
        COALESCE(
          managers_who_are_study_participants.email,
          lss.to_user_uuid
        ) as manager_email,
        p.first_name,
        p.last_name,
        sps.removal_from_study ->> 'removal_datetime' IS NOT NULL AS removed_from_study,
        lss.received ->> 'datetime' as received_datetime,
        num_targeted_masks,
        total_unique_masks_fit_tested.num_targeted_unique_masks_fit_tested,
        ROUND((num_targeted_unique_masks_fit_tested::float / num_targeted_masks * 100)::numeric, 2) AS fit_testing_percent_complete,
        CASE WHEN demog_present_counts IS NULL THEN 0 ELSE demog_present_counts END AS demog_present_counts,
        CASE WHEN fm_present_counts IS NULL THEN 0 ELSE fm_present_counts END AS fm_present_counts,
        ROUND(CAST(CASE WHEN fm_present_counts IS NULL THEN 0 ELSE fm_present_counts END::float / #{FacialMeasurement::COLUMNS.size} * 100 AS NUMERIC), 2) AS fm_percent_complete,
        ROUND(CAST(CASE WHEN demog_present_counts IS NULL THEN 0 ELSE demog_present_counts END::float / #{Profile::STRING_DEMOG_FIELDS.size + Profile::NUM_DEMOG_FIELDS.size} * 100 AS NUMERIC), 2) AS demog_percent_complete,
        managed_users.*, fm.created_at, fm.updated_at

        FROM latest_shipping_statuses lss
        LEFT JOIN latest_sent_masks_counts lsmc
          ON lss.to_user_uuid = lsmc.us_uuid
        LEFT JOIN
          managers_who_are_study_participants
          ON managers_who_are_study_participants.email = lsmc.us_uuid
        FULL OUTER JOIN managed_users
          ON managed_users.manager_id = managers_who_are_study_participants.id
        LEFT JOIN profile_with_demog_fields_present_count p
          ON managed_users.managed_id = p.user_id
        LEFT JOIN latest_facial_measurement_with_present_counts fm
          ON fm.user_id = managed_users.managed_id
        LEFT JOIN total_unique_masks_fit_tested
          ON total_unique_masks_fit_tested.user_id = managed_users.managed_id
        LEFT JOIN study_participant_statuses sps
          ON sps.participant_uuid = lss.to_user_uuid

        #{where}
        ORDER BY manager_email
        SQL
      ).to_json
    )
  end
end
