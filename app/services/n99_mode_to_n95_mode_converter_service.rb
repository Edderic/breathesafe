# frozen_string_literal: true

class N99ModeToN95ModeConverterService
  class << self
    def n99_exercises
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_exercises
        SQL
      )
    end

    def n99_exercise_name_and_fit_factors
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_exercise_name_and_fit_factors
        SQL
      )
    end

    def n99_filtration_efficiency_from_exercises
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_filtration_efficiency_from_exercises
        SQL
      )
    end

    def aaron_sealed_fit_factors
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM aaron_sealed_fit_factors
        SQL
      )
    end

    def aarons_as_exercise
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM aarons_as_exercise
        SQL
      )
    end

    def combined_fe_estimates
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM combined_fe_estimates
        SQL
      )
    end

    def avg_sealed_ffs
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM avg_sealed_ffs
        SQL
      )
    end

    def avg_sealed_ffs_as_exercise
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM avg_sealed_ffs_as_exercise
        SQL
      )
    end

    def exercise_fit_factors_with_avg_sealed_ff
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM exercise_fit_factors_with_avg_sealed_ff
        SQL
      )
    end

    def max_fit_factor_from_fit_tests
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM max_fit_factor_from_fit_tests
        SQL
      )
    end

    def with_final_sealed_ff
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM with_final_sealed_ff
        SQL
      )
    end

    def n95_mode_estimate_for_exercises
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n95_mode_estimate_for_exercises
        SQL
      )
    end

    def n95_mode_estimates
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n95_mode_estimates
        SQL
      )
    end

    def n99_mode_fit_tests_missing_fe
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_mode_fit_tests_missing_fe
        SQL
      )
    end

    def unioned
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM unioned
        SQL
      )
    end

    def n99_fit_tests_at_least_partially_filled
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_fit_tests_at_least_partially_filled
        SQL
      )
    end

    def n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT * FROM n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency
        SQL
      )
    end

    def avg_sealed_ffs_sql(mask_id_clause)
      <<-SQL
          n99_exercises AS (
              SELECT * FROM fit_tests
              WHERE results -> 'quantitative' ->> 'testing_mode' = 'N99'
              #{mask_id_clause}
          ),
          n99_exercise_name_and_fit_factors AS (
              SELECT n99_exercises.id,
              mask_id,
              exercises ->> 'name' AS exercise_name,
              CASE#{' '}
                WHEN exercises ->> 'fit_factor' = '' THEN NULL
                ELSE (exercises ->> 'fit_factor')::numeric#{' '}
              END as exercise_fit_factor
              FROM n99_exercises, jsonb_array_elements(results -> 'quantitative' -> 'exercises') as exercises
          ), n99_filtration_efficiency_from_exercises AS (
              SELECT * FROM n99_exercise_name_and_fit_factors
              WHERE exercise_name = 'Normal breathing (SEALED)'
              AND exercise_fit_factor IS NOT NULL
          ), n99_non_filtration_efficiency_from_exercise AS (
              SELECT * FROM n99_exercise_name_and_fit_factors
              WHERE exercise_name != 'Normal breathing (SEALED)'
              AND exercise_fit_factor IS NOT NULL
          ), n99_fit_tests_at_least_partially_filled AS (
              SELECT id, COUNT(*) as num_exercises_filled
              FROM n99_non_filtration_efficiency_from_exercise
              WHERE exercise_fit_factor IS NOT NULL
              GROUP BY 1
          ),

          aaron_sealed_fit_factors AS (
              SELECT masks.id,
               mask_filtration_efficiencies -> 'filtration_efficiency_notes' AS notes,
               CASE WHEN (mask_filtration_efficiencies ->> 'filtration_efficiency_percent') = '' THEN NULL ELSE (mask_filtration_efficiencies ->> 'filtration_efficiency_percent') END::numeric / 100 AS aaron_filtration_efficiency,
               mask_filtration_efficiencies -> 'filtration_efficiency_source' AS source
               FROM masks, jsonb_array_elements(filtration_efficiencies) AS mask_filtration_efficiencies
              WHERE mask_filtration_efficiencies ->> 'filtration_efficiency_notes' ILIKE '%aaron%'
          ), aarons_as_exercise AS (
            SELECT NULL as id,
              id AS mask_id,
              'Normal breathing (SEALED)' AS exercise_name,
              1 / (1 - aaron_filtration_efficiency) AS exercise_fit_factor
            FROM aaron_sealed_fit_factors
          ), combined_fe_estimates AS (
            SELECT mask_id, exercise_name, exercise_fit_factor FROM aarons_as_exercise
            UNION
            SELECT mask_id, exercise_name, exercise_fit_factor FROM n99_filtration_efficiency_from_exercises
          ), avg_sealed_ffs AS (
            SELECT mask_id, AVG(exercise_fit_factor) AS avg_sealed_ff, COUNT(*) AS count_sealed_fit_factor
            FROM combined_fe_estimates
            GROUP BY 1
          )
      SQL
    end

    def n95_mode_estimates_sql(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ''

      <<-SQL
          WITH
          #{avg_sealed_ffs_sql(mask_id_clause)},
          avg_sealed_ffs_as_exercise AS (
            SELECT mask_id, 'averaged_sealed_ff' AS exercise_name, avg_sealed_ff AS exercise_fit_factor
            FROM avg_sealed_ffs
          ),

          exercise_fit_factors_with_avg_sealed_ff AS (
            SELECT n99_exercise_name_and_fit_factors.*, avg_sealed_ff
            FROM n99_exercise_name_and_fit_factors
            INNER JOIN avg_sealed_ffs ON avg_sealed_ffs.mask_id = n99_exercise_name_and_fit_factors.mask_id
            AND exercise_fit_factor IS NOT NULL
            AND exercise_name NOT IN ('Normal breathing (SEALED)', 'Talking')
          ),
          max_fit_factor_from_fit_tests AS (
              SELECT exercise_fit_factors_with_avg_sealed_ff.id,
                MAX(exercise_fit_factor) as max_ff_across_exercises
                -- CASE WHEN MAX(exercise_fit_factor) > avg_sealed_ff THEN MAX(exercise_fit_factor) + 1
                  -- ELSE avg_sealed_ff END AS no_div_zero_avg_sealed_ff
              FROM exercise_fit_factors_with_avg_sealed_ff
              GROUP BY 1
          ), with_final_sealed_ff AS (
            SELECT exercise_fit_factors_with_avg_sealed_ff.*, max_fit_factor_from_fit_tests.max_ff_across_exercises ,
            CASE WHEN max_ff_across_exercises >= avg_sealed_ff
              THEN max_ff_across_exercises + 1
              ELSE avg_sealed_ff
              END AS final_sealed_ff

              FROM max_fit_factor_from_fit_tests
              INNER JOIN exercise_fit_factors_with_avg_sealed_ff
                ON max_fit_factor_from_fit_tests.id = exercise_fit_factors_with_avg_sealed_ff.id
          ), n95_mode_estimate_for_exercises AS (
            SELECT id,
              (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff) AS normalized_exposure_reduction,
              1 / (1 - (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff)) AS n95_mode_estimate,
              1 / (1 / (1 - (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff)) ) AS n95_mode_inverse
            FROM with_final_sealed_ff
            WHERE exercise_name != 'Talking'

          ), n95_mode_estimates AS (
            SELECT id,
             COUNT(*) AS n,
             SUM(n95_mode_inverse) AS denominator,
             COUNT(*) / SUM(n95_mode_inverse) * 2 AS n95_mode_hmff,
             COUNT(*) / SUM(n95_mode_inverse) * 2 >= 100 AS qlft_pass
            FROM n95_mode_estimate_for_exercises
            GROUP BY 1
          ),
          n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency AS (
              SELECT id
              FROM n99_fit_tests_at_least_partially_filled

              EXCEPT

              SELECT id
              FROM n99_filtration_efficiency_from_exercises
          ), n99_mode_fit_test_exercises_with_data_but_missing_filtration_efficiency AS (
            SELECT * FROM
            n99_exercise_name_and_fit_factors
            WHERE id IN (SELECT id FROM n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency)
          ), n99_mode_fit_tests_missing_fe AS (
            SELECT id,
              COUNT(*) AS n,
              NULL::numeric as denominator,
              NULL::numeric AS n95_mode_hmff,
              NULL::bool AS qlft_pass
            FROM n99_mode_fit_test_exercises_with_data_but_missing_filtration_efficiency
            GROUP BY id
          ), unioned AS (
            SELECT
              id, n, denominator, n95_mode_hmff, qlft_pass
            FROM n99_mode_fit_tests_missing_fe
            UNION
            SELECT id, n, denominator, n95_mode_hmff, qlft_pass
            FROM n95_mode_estimates
          )
      SQL
    end

    def call(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ''

      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH
          #{FacialMeasurementOutliersService.latest_measurements_sql},
          #{FacialMeasurementOutliersService.measurement_stats_sql_without_bounds},
          #{avg_sealed_ffs_sql(mask_id_clause)},
          avg_sealed_ffs_as_exercise AS (
            SELECT mask_id, 'averaged_sealed_ff' AS exercise_name, avg_sealed_ff AS exercise_fit_factor
            FROM avg_sealed_ffs
          ),

          exercise_fit_factors_with_avg_sealed_ff AS (
            SELECT n99_exercise_name_and_fit_factors.*, avg_sealed_ff
            FROM n99_exercise_name_and_fit_factors
            INNER JOIN avg_sealed_ffs ON avg_sealed_ffs.mask_id = n99_exercise_name_and_fit_factors.mask_id
            AND exercise_fit_factor IS NOT NULL
            AND exercise_name NOT IN ('Normal breathing (SEALED)', 'Talking')
          ),
          max_fit_factor_from_fit_tests AS (
              SELECT exercise_fit_factors_with_avg_sealed_ff.id,
                MAX(exercise_fit_factor) as max_ff_across_exercises
                -- CASE WHEN MAX(exercise_fit_factor) > avg_sealed_ff THEN MAX(exercise_fit_factor) + 1
                  -- ELSE avg_sealed_ff END AS no_div_zero_avg_sealed_ff
              FROM exercise_fit_factors_with_avg_sealed_ff
              GROUP BY 1
          ), with_final_sealed_ff AS (
            SELECT exercise_fit_factors_with_avg_sealed_ff.*, max_fit_factor_from_fit_tests.max_ff_across_exercises ,
            CASE WHEN max_ff_across_exercises >= avg_sealed_ff
              THEN max_ff_across_exercises + 1
              ELSE avg_sealed_ff
              END AS final_sealed_ff

              FROM max_fit_factor_from_fit_tests
              INNER JOIN exercise_fit_factors_with_avg_sealed_ff
                ON max_fit_factor_from_fit_tests.id = exercise_fit_factors_with_avg_sealed_ff.id
          ), n95_mode_estimate_for_exercises AS (
            SELECT id,
              (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff) AS normalized_exposure_reduction,
              1 / (1 - (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff)) AS n95_mode_estimate,
              1 / (1 / (1 - (1 - 1 / exercise_fit_factor) / (1 - 1 / final_sealed_ff)) ) AS n95_mode_inverse
            FROM with_final_sealed_ff
            WHERE exercise_name != 'Talking'

          ), n95_mode_estimates AS (
            SELECT id,
             COUNT(*) AS n,
             SUM(n95_mode_inverse) AS denominator,
             COUNT(*) / SUM(n95_mode_inverse) * 2 AS n95_mode_hmff,
             COUNT(*) / SUM(n95_mode_inverse) * 2 >= 100 AS qlft_pass
            FROM n95_mode_estimate_for_exercises
            GROUP BY 1
          ),
          n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency AS (
              SELECT id
              FROM n99_fit_tests_at_least_partially_filled

              EXCEPT

              SELECT id
              FROM n99_filtration_efficiency_from_exercises
          ), n99_mode_fit_test_exercises_with_data_but_missing_filtration_efficiency AS (
            SELECT * FROM
            n99_exercise_name_and_fit_factors
            WHERE id IN (SELECT id FROM n99_mode_fit_tests_ids_with_data_but_missing_filtration_efficiency)
          ), n99_mode_fit_tests_missing_fe AS (
            SELECT id,
              COUNT(*) AS n,
              NULL::numeric as denominator,
              NULL::numeric AS n95_mode_hmff,
              NULL::bool AS qlft_pass
            FROM n99_mode_fit_test_exercises_with_data_but_missing_filtration_efficiency
            GROUP BY id
          ), unioned AS (
            SELECT
              id, n, denominator, n95_mode_hmff, qlft_pass
            FROM n99_mode_fit_tests_missing_fe
            UNION
            SELECT id, n, denominator, n95_mode_hmff, qlft_pass
            FROM n95_mode_estimates
          )

          SELECT unioned.*,
            (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
            masks.unique_internal_model_code,
            masks.perimeter_mm,
            masks.strap_type,
            masks.style,
            #{FacialMeasurement::COLUMNS.join(',')},
            #{FacialMeasurement::COLUMNS.map do |col|
              <<-SQL
                CASE
                  WHEN fm.#{col} IS NULL THEN NULL
                  WHEN ms.stddev_#{col} = 0 OR ms.stddev_#{col} IS NULL THEN NULL
                  ELSE (fm.#{col} - ms.avg_#{col}) / ms.stddev_#{col}
                END as #{col}_z_score
              SQL
            end.join(',')},
            '#{self}' AS source,
            mask_id,
            ft.user_id
          FROM unioned
          LEFT JOIN fit_tests ft
            ON unioned.id = ft.id
          INNER JOIN masks ON ft.mask_id = masks.id
          LEFT JOIN facial_measurements fm
            ON ft.facial_measurement_id = fm.id
          CROSS JOIN measurement_stats ms
        SQL
      )
    end
  end
end
