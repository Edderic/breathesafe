class Mask < ApplicationRecord
  belongs_to :author, class_name: 'User'
  validates_presence_of :unique_internal_model_code
  validates_uniqueness_of :unique_internal_model_code

  def self.find_targeted_but_untested_masks(manager_id)
    results = Mask.connection.exec_query(
      <<-SQL
      WITH scoped_to_manager AS (
        SELECT * FROM managed_users WHERE manager_id = #{manager_id}
      ), targeted_masks AS (
        SELECT * FROM masks
        WHERE JSON_ARRAY_LENGTH(payable_datetimes) > 0
      ), fit_tests_grouped_by_managed_id_and_mask_id AS (
        SELECT user_id, mask_id FROM fit_tests
        INNER JOIN scoped_to_manager
        ON (scoped_to_manager.managed_id = fit_tests.user_id)
        GROUP BY 1,2
      ), user_mask_cross_join AS (
        SELECT scoped_to_manager.managed_id, targeted_masks.id as mask_id, fit_tests.id as fit_test_id
        FROM scoped_to_manager
          CROSS JOIN targeted_masks
          LEFT JOIN fit_tests
            ON scoped_to_manager.managed_id = fit_tests.user_id
            AND targeted_masks.id = fit_tests.mask_id
      ), cross_join AS (
        SELECT managed_id, mask_id, COUNT(DISTINCT fit_test_id)
        FROM user_mask_cross_join

        GROUP BY 1,2
      )

      SELECT cross_join.*, masks.* FROM cross_join
      INNER JOIN masks ON masks.id = cross_join.mask_id
      SQL
    )

    json_parsed = JSON.parse(results.to_json)
    FitTest.json_parse(json_parsed, ['image_urls'])
  end

  def self.find_payable_on(date)
    masks = Mask.all

    masks.select do |m|
      m.payable_datetimes.any? do |dts|
        if dts['end_datetime']
          dts['start_datetime'].to_datetime < date && dts['end_datetime'].to_datetime >= date
        else
          dts['start_datetime'].to_datetime < date
        end
      end
    end
  end

  def self.average_filtration_efficiencies_sql
    <<-SQL
        #{N99ModeToN95ModeConverterService.avg_sealed_ffs_sql("")}
    SQL
  end

  def self.with_aggregations(mask_ids=nil)
    if mask_ids
      mask_id_clause = Mask.sanitize_sql_array(["WHERE m.id IN (?)", mask_ids])
    else
      mask_id_clause = ""
    end

    result = Mask.connection.exec_query(
      <<-SQL
        WITH fit_test_counts_per_mask AS (
          SELECT m.id as mask_id, COUNT(ft.id) AS fit_test_count
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id
        ),

        #{self.average_filtration_efficiencies_sql},

        breathability_measurements AS (
            SELECT m.id, b ->> 'breathability_pascals' as breathability_pascals,
                b ->> 'breathability_pascals_notes' as breathability_pascals_notes
            FROM masks m, jsonb_array_elements(
                  CASE
                    WHEN jsonb_typeof(breathability) = 'array' THEN breathability
                    ELSE jsonb_build_array(breathability)
                  END
            ) AS b
        ), breathability_aggregates AS (
            SELECT id,
              COUNT(*) AS count_breathability,
              AVG(breathability_pascals::numeric) AS avg_breathability_pa
            FROM breathability_measurements
            GROUP BY 1
        ),

        unique_fit_tester_counts_per_mask AS (
          SELECT m.id AS mask_id, COUNT(DISTINCT fm.user_id) AS unique_fit_testers_count
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          LEFT JOIN facial_measurements fm
          ON (fm.id = ft.facial_measurement_id)
          GROUP BY m.id
        ), unique_fit_testers_per_mask AS (
          SELECT m.id AS mask_id,
            fm.user_id,
            MIN(ft.created_at) AS created_at
          FROM masks m
          LEFT JOIN fit_tests ft
            ON (ft.mask_id = m.id)
          LEFT JOIN facial_measurements fm
            ON (fm.id = ft.facial_measurement_id)
          GROUP BY 1, 2
        ), demographic_breakdown AS (
          SELECT m.id,
            SUM(
              CASE WHEN p.race_ethnicity = 'American Indian or Alaskan Native'
                THEN 1
              ELSE 0
              END
            ) AS american_indian_or_alaskan_native_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'Asian / Pacific Islander'
                THEN 1
              ELSE 0
              END
            ) AS asian_pacific_islander_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'Black or African American'
                THEN 1
              ELSE 0
              END
            ) AS black_african_american_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'Hispanic'
                THEN 1
              ELSE 0
              END
            ) AS hispanic_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'White / Caucasian'
                THEN 1
              ELSE 0
              END
            ) AS white_caucasian_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'Multiple ethnicity / Other'
                THEN 1
              ELSE 0
              END
            ) AS multiple_ethnicity_other_count,
            SUM(
              CASE WHEN p.race_ethnicity = 'Prefer not to disclose'
                THEN 1
              ELSE 0
              END
            ) AS prefer_not_to_disclose_race_ethnicity_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'Cisgender male'
                THEN 1
              ELSE 0
              END
            ) AS cisgender_male_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'Cisgender female'
                THEN 1
              ELSE 0
              END
            ) AS cisgender_female_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'MTF transgender'
                THEN 1
              ELSE 0
              END
            ) AS mtf_transgender_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'FTM transgender'
                THEN 1
              ELSE 0
              END
            ) AS ftm_transgender_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'Intersex'
                THEN 1
              ELSE 0
              END
            ) AS intersex_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'Prefer not to disclose'
                THEN 1
              ELSE 0
              END
            ) AS prefer_not_to_disclose_gender_sex_count,
            SUM(
              CASE WHEN p.gender_and_sex = 'Other'
                THEN 1
              ELSE 0
              END
            ) AS other_gender_sex_count,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 2 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 4
                THEN 1
              ELSE 0
              END
            ) AS age_between_2_and_4,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 4 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 6
                THEN 1
              ELSE 0
              END
            ) AS age_between_4_and_6,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 6 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 8
                THEN 1
              ELSE 0
              END
            ) AS age_between_6_and_8,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 8 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 10
                THEN 1
              ELSE 0
              END
            ) AS age_between_8_and_10,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 10 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 12
                THEN 1
              ELSE 0
              END
            ) AS age_between_10_and_12,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 12 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 14
                THEN 1
              ELSE 0
              END
            ) AS age_between_12_and_14,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 14 AND EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth < 18
                THEN 1
              ELSE 0
              END
            ) AS age_between_14_and_18,
            SUM(
              CASE WHEN EXTRACT(YEAR FROM ft.created_at) - p.year_of_birth >= 18
                THEN 1
              ELSE 0
              END
            ) AS age_adult,
            SUM(
              CASE WHEN p.year_of_birth IS NULL AND p.user_id IS NOT NULL
                THEN 1
              ELSE 0
              END
            ) AS prefer_not_to_disclose_age_count

          FROM masks m
          LEFT JOIN unique_fit_testers_per_mask ft
            ON (ft.mask_id = m.id)
          LEFT JOIN profiles p
            ON (p.user_id = ft.user_id)
          #{mask_id_clause}
          GROUP BY m.id
        )

        SELECT masks.id,
          masks.*,
          demographic_breakdown.*,
          CASE WHEN fit_test_count IS NULL THEN 0 ELSE fit_test_count END AS fit_test_count,
          unique_fit_tester_counts_per_mask.*,
          avg_sealed_ffs.avg_sealed_ff AS avg_sealed_fit_factor,
          avg_sealed_ffs.count_sealed_fit_factor,
          breathability_aggregates.avg_breathability_pa,
          count_breathability
        FROM
          masks LEFT JOIN demographic_breakdown
            ON masks.id = demographic_breakdown.id
          LEFT JOIN fit_test_counts_per_mask ON (fit_test_counts_per_mask.mask_id = demographic_breakdown.id)
          LEFT JOIN unique_fit_tester_counts_per_mask
            ON (unique_fit_tester_counts_per_mask.mask_id = demographic_breakdown.id)
          LEFT JOIN avg_sealed_ffs
            ON masks.id = avg_sealed_ffs.mask_id
          LEFT JOIN breathability_aggregates
            ON masks.id = breathability_aggregates.id

      SQL
    ).to_a

    result.each do |x|
      if x['image_urls']
        x['image_urls'] = [x['image_urls'].gsub(/{|}/, "").gsub(/\"/, "")]
      else
        x['image_urls'] = [""]
      end

      if x['breathability']
        x['breathability'] = JSON.parse(x['breathability'])
      end

      if x['filtration_efficiencies']
        x['filtration_efficiencies'] = JSON.parse(x['filtration_efficiencies'])
      end

      if x['where_to_buy_urls']
        x['where_to_buy_urls'] = [x['where_to_buy_urls'].gsub(/{|}/, "")]
      else
        x['where_to_buy_urls'] = [""]
      end

      x['payable_datetimes'] = JSON.parse(x['payable_datetimes'])
      x['colors'] = JSON.parse(x['colors'])
    end

    result
  end

  def self.with_privacy_aggregations(mask_ids=nil)
    aggregations = self.with_aggregations(mask_ids=mask_ids)
    race_ethnicity_options = [
      'american_indian_or_alaskan_native_count',
      'asian_pacific_islander_count',
      'black_african_american_count',
      'hispanic_count',
      'white_caucasian_count',
      'multiple_ethnicity_other_count',
    ]

    gender_sex_options = [
      'cisgender_male_count',
      'cisgender_female_count',
      'mtf_transgender_count',
      'ftm_transgender_count',
      'intersex_count',
      'other_gender_sex_count'
    ]

    age_options = [
      'age_between_2_and_4',
      'age_between_4_and_6',
      'age_between_6_and_8',
      'age_between_8_and_10',
      'age_between_10_and_12',
      'age_between_12_and_14',
      'age_between_14_and_18',
      'age_adult'
    ]

    threshold = 5
    hash = {}

    aggregations.each do |r|
      r['prefer_not_to_disclose_race_ethnicity_count'] ||= 0
      r['prefer_not_to_disclose_gender_sex_count'] ||= 0
      r['prefer_not_to_disclose_age_count'] ||= 0

      race_ethnicity_options.each do |re|
        r[re] ||= 0
        if r[re] < threshold
          r['prefer_not_to_disclose_race_ethnicity_count'] += r[re]
          r[re] = 0
        end
      end

      gender_sex_options.each do |gs|
        r[gs] ||= 0

        if r[gs] < threshold
          r['prefer_not_to_disclose_gender_sex_count'] += r[gs]
          r[gs] = 0
        end
      end

      age_options.each do |a|
        r[a] ||= 0

        if r[a] < threshold
          r['prefer_not_to_disclose_age_count'] += r[a]
          r[a] = 0
        end
      end

      hash[r['id']] = r
    end

    if mask_ids
      masks = Mask.where(id: mask_ids)
    else
      masks = Mask.all
    end

    masks.map do |m|
      m_data = JSON.parse(m.to_json)

      m_data.merge(hash[m.id])
    end
  end
end

