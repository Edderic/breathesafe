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

    def n95_mode_estimates_sql
      <<-SQL
          WITH n99_exercises AS (
              SELECT * FROM fit_tests
              WHERE results -> 'quantitative' ->> 'testing_mode' = 'N99'
          ), n99_exercise_name_and_fit_factors AS (
              SELECT n99_exercises.id,
              mask_id,
              exercises ->> 'name' AS exercise_name,
              (exercises ->> 'fit_factor')::numeric as exercise_fit_factor
              FROM n99_exercises, jsonb_array_elements(results -> 'quantitative' -> 'exercises') as exercises
          ), n99_filtration_efficiency_from_exercises AS (
              SELECT * FROM n99_exercise_name_and_fit_factors
              WHERE exercise_name = 'Normal breathing (SEALED)'
              AND exercise_fit_factor IS NOT NULL
          ), aaron_sealed_fit_factors AS (
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
            SELECT mask_id, AVG(exercise_fit_factor) AS avg_sealed_ff
            FROM combined_fe_estimates
            GROUP BY 1
          ), avg_sealed_ffs_as_exercise AS (
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
          ), n95_mode_estimates_and_facial_measurements AS (
            SELECT n95_mode_estimates.*,
             #{FacialMeasurement::COLUMNS.join(",")}

             FROM n95_mode_estimates
              INNER JOIN fit_tests ft
                ON ft.id = n95_mode_estimates.id
              LEFT JOIN facial_measurements fm
                ON ft.facial_measurement_id = fm.id
          )
      SQL
    end

    def call
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          #{n95_mode_estimates_sql}
          SELECT *
          FROM n95_mode_estimates_and_facial_measurements
        SQL
      )
    end
  end
end
