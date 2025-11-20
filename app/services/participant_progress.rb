# frozen_string_literal: true

class ParticipantProgress
  # tracks the progress of a participant in the Mask Recommender Based on
  # Facial Features
  #
  def self.facial_measurements_present_sql
    FacialMeasurement::COLUMNS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != 0 THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end

  def self.string_demographics_present_sql
    Profile::STRING_DEMOG_FIELDS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != '' THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end

  def self.numeric_demographics_present_sql
    Profile::NUM_DEMOG_FIELDS.map do |c|
      "CASE WHEN #{c} IS NOT NULL AND #{c} != 0 THEN 1 ELSE 0 END AS #{c}_present"
    end.join(',')
  end

  def self.demographics_present_sql
    "#{string_demographics_present_sql},#{numeric_demographics_present_sql}"
  end

  def self.demographics_present_counts
    (Profile::STRING_DEMOG_FIELDS + Profile::NUM_DEMOG_FIELDS).map do |c| # rubocop:disable Style/StringConcatenation
      "#{c}_present"
    end.join('+') + ' AS demog_present_counts'
  end

  def self.facial_measurements_present_counts
    FacialMeasurement::COLUMNS.map do |c| # rubocop:disable Style/StringConcatenation
      "#{c}_present"
    end.join('+') + ' AS fm_present_counts'
  end

  def self.recommender_measurements_select_sql
    FacialMeasurement::RECOMMENDER_COLUMNS.map do |column_name|
      "latest_facial_measurements_for_users.#{column_name}"
    end.join(",\n        ")
  end

  def self.call(manager_id:)
    user = User.find(manager_id)
    manager_filter = user.admin? ? '' : "WHERE manager_id = #{manager_id}"

    # Execute the complex query
    results = JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH managed_by_manager AS (
            SELECT * FROM managed_users
            #{manager_filter}
          ), latest_facial_measurement_created_at AS (
          SELECT user_id, MAX(created_at) AS created_at
          FROM facial_measurements fm
          GROUP BY 1
        ), latest_facial_measurements_for_users AS (
          SELECT fm.*,
          #{facial_measurements_present_sql}
          FROM facial_measurements fm
          INNER JOIN latest_facial_measurement_created_at lfm
          ON fm.user_id = lfm.user_id
          AND fm.created_at = lfm.created_at
        ), latest_facial_measurements_for_users_counts AS (
          SELECT id,
           created_at,
           updated_at,
           #{facial_measurements_present_counts},
           user_id
          FROM latest_facial_measurements_for_users
        ),

        #{FacialMeasurement.missing_ratio_sql},

        #{FacialMeasurement.arkit_percent_complete_sql},

        profile_with_demog_fields_present AS (
          SELECT *, #{demographics_present_sql}
          FROM profiles

        ), profile_with_demog_fields_present_count AS (
          SELECT *,
            #{demographics_present_counts}
          FROM profile_with_demog_fields_present
        ),
        masks_shipped AS (
          SELECT to_user_uuid, mask_uuid
          FROM shipping_statuses ss
          INNER JOIN shipping_status_joins ssj
            ON ssj.shipping_uuid = ss.uuid
          INNER JOIN mask_kit_statuses mks
            ON mks.uuid = ssj.shippable_uuid
        ),
        targeted_masks AS (
          SELECT * FROM masks_shipped
          INNER JOIN masks ON masks.id = masks_shipped.mask_uuid
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
        mask_shipped_counts AS (
          SELECT to_user_uuid, count(*) AS num_targeted_masks
          FROM masks_shipped
          GROUP BY 1
        ), sent_masks AS (
            SELECT distinct on (mask_uuid)
                us.uuid as us_uuid,
                mask_uuid
            FROM user_statuses us
            LEFT JOIN shipping_statuses ss
            ON ss.to_user_uuid = us.uuid
            LEFT JOIN shipping_status_joins ssj
            ON ssj.shipping_uuid = ss.uuid
            LEFT JOIN mask_kit_statuses mks
            ON mks.uuid = ssj.shippable_uuid
            WHERE ssj.shippable_type = 'MaskKit'
          ), num_masks_tested AS (
          -- TODO: correctly calculate num_unique_masks_tested
            SELECT user_id, COUNT(DISTINCT mask_id) AS num_unique_masks_tested
            FROM managed_by_manager INNER JOIN fit_tests ft ON (ft.user_id = managed_by_manager.managed_id)
          GROUP BY 1
        )



        SELECT
        managers.email as manager_email,
        p.first_name,
        p.last_name,
        #{recommender_measurements_select_sql},
        -- num_targeted_masks,
        total_unique_masks_fit_tested.num_targeted_unique_masks_fit_tested,
        -- ROUND((num_targeted_unique_masks_fit_tested::float / num_targeted_masks * 100)::numeric, 2) AS fit_testing_percent_complete,
        COALESCE(apc.percent_complete, 0.0) AS fm_percent_complete,
        ROUND((demog_present_counts::float / #{Profile::STRING_DEMOG_FIELDS.size + Profile::NUM_DEMOG_FIELDS.size} * 100)::numeric, 2) AS demog_percent_complete,
        mu.*, fm.created_at, fm.updated_at,
        num_masks_tested.num_unique_masks_tested

        FROM users AS managers
        INNER JOIN managed_by_manager mu ON (mu.manager_id = managers.id)

        LEFT JOIN num_masks_tested ON (num_masks_tested.user_id = mu.managed_id)

        LEFT JOIN latest_facial_measurements_for_users ON latest_facial_measurements_for_users.user_id =
          mu.managed_id

        LEFT JOIN facial_measurement_missing_ratio AS fmmr ON (fmmr.id = latest_facial_measurements_for_users.id)

        LEFT JOIN arkit_percent_complete AS apc ON (apc.id = latest_facial_measurements_for_users.id)

        LEFT JOIN profile_with_demog_fields_present_count p
          ON mu.managed_id = p.user_id
        LEFT JOIN latest_facial_measurements_for_users_counts fm
          ON fm.user_id = mu.managed_id
        LEFT JOIN total_unique_masks_fit_tested
          ON total_unique_masks_fit_tested.user_id = mu.managed_id


        ORDER BY manager_email
        SQL
      ).to_json
    )

    managed_ids = results.map { |result| result['managed_id'] }.compact
    profiles_by_user_id = Profile.where(user_id: managed_ids).index_by(&:user_id)

    results.each do |result|
      profile = profiles_by_user_id[result['managed_id']]
      next unless profile

      result['first_name'] = profile.first_name
      result['last_name'] = profile.last_name
    end

    results
  end
end
