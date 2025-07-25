class N95ModeService
  def self.call(mask_id: nil)
    mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ""

    # Looks for FitTests where testing_mode is 'N95'
    # Computes the harmonic mean fit factor (hmff) for all the exercises,
    # with the exception of Normal breathing (SEALED)
    ActiveRecord::Base.connection.exec_query(
      <<-SQL
        WITH
        #{FacialMeasurementOutliersService.latest_measurements_sql},
        #{FacialMeasurementOutliersService.measurement_stats_sql_without_bounds}
        ,
        n95_exercises AS (
            SELECT * FROM fit_tests
            WHERE results -> 'quantitative' ->> 'testing_mode' = 'N95'
            #{mask_id_clause}
        ), n95_exercise_name_and_fit_factors AS (
            SELECT n95_exercises.id,
            mask_id,
            exercises ->> 'name' AS exercise_name,
            CASE 
              WHEN exercises ->> 'fit_factor' = '' THEN NULL
              ELSE (exercises ->> 'fit_factor')::numeric 
            END as exercise_fit_factor,
            CASE 
              WHEN exercises ->> 'fit_factor' = '' THEN NULL
              WHEN (exercises ->> 'fit_factor')::numeric IS NULL THEN NULL
              ELSE 1 / (exercises ->> 'fit_factor')::numeric 
            END AS inverse_exercise_fit_factor
            FROM n95_exercises, jsonb_array_elements(results -> 'quantitative' -> 'exercises') as exercises
            WHERE exercises ->> 'name' != 'Normal breathing (SEALED)'
        ), n95_mode_experimentals AS (
            SELECT id,
              COUNT(*) as n,
              SUM(inverse_exercise_fit_factor) as denominator,
              COUNT(*) / SUM(inverse_exercise_fit_factor) as n95_mode_hmff,
              COUNT(*) / SUM(inverse_exercise_fit_factor) >= 100 AS qlft_pass

            FROM n95_exercise_name_and_fit_factors
            GROUP BY 1
        )

        SELECT n95_mode_experimentals.*,
          fit_tests.mask_id,
          (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
          '#{self}' AS source,
          fit_tests.user_id,
          masks.unique_internal_model_code,
          masks.perimeter_mm,
          masks.strap_type,
          masks.style,
          #{FacialMeasurement::COLUMNS.join(', ')},
          #{FacialMeasurement::COLUMNS.map do |col|
            <<-SQL
              CASE
                WHEN facial_measurements.#{col} IS NULL THEN NULL
                WHEN ms.stddev_#{col} = 0 OR ms.stddev_#{col} IS NULL THEN NULL
                ELSE (facial_measurements.#{col} - ms.avg_#{col}) / ms.stddev_#{col}
              END as #{col}_z_score
            SQL
          end.join(',')}
        FROM n95_mode_experimentals
        INNER JOIN fit_tests ON fit_tests.id = n95_mode_experimentals.id
        INNER JOIN masks ON fit_tests.mask_id = masks.id
        LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
        CROSS JOIN measurement_stats ms
      SQL
    )
  end
end
