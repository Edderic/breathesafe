# frozen_string_literal: true

class N95ModeService
  def self.call(mask_id: nil)
    mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ''

    # Looks for FitTests where testing_mode is 'N95'
    # Computes the harmonic mean fit factor (hmff) for all the exercises,
    # with the exception of Normal breathing (SEALED)
    results = ActiveRecord::Base.connection.exec_query(
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
            CASE#{' '}
              WHEN exercises ->> 'fit_factor' = '' THEN NULL
              ELSE (exercises ->> 'fit_factor')::numeric#{' '}
            END as exercise_fit_factor,
            CASE#{' '}
              WHEN exercises ->> 'fit_factor' = '' THEN NULL
              WHEN (exercises ->> 'fit_factor')::numeric IS NULL THEN NULL
              ELSE 1 / (exercises ->> 'fit_factor')::numeric#{' '}
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
          fit_tests.user_seal_check::jsonb AS user_seal_check,
          (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
          '#{self}' AS source,
          fit_tests.user_id,
          fit_tests.created_at,
          masks.unique_internal_model_code,
          masks.perimeter_mm,
          masks.strap_type,
          masks.style,
          fit_tests.facial_measurement_id,
          facial_measurements.arkit
        FROM n95_mode_experimentals
        INNER JOIN fit_tests ON fit_tests.id = n95_mode_experimentals.id
        INNER JOIN masks ON fit_tests.mask_id = masks.id
        LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
      SQL
    )

    # Compute aggregated ARKit measurements in Ruby
    facial_measurements_with_aggregated = results.map do |row|
      facial_measurement_id = row['facial_measurement_id']
      arkit_data = row['arkit']

      aggregated = if facial_measurement_id && arkit_data && !arkit_data.to_s.strip.empty?
                     begin
                       # Parse JSONB if it's a string, otherwise use as-is
                       parsed_arkit = if arkit_data.is_a?(String)
                                        JSON.parse(arkit_data)
                                      else
                                        arkit_data
                                      end
                       temp_fm = FacialMeasurement.new(arkit: parsed_arkit)
                       temp_fm.aggregated_arkit_measurements
                     rescue StandardError
                       # If parsing fails, return nil values
                       {
                         nose_mm: nil,
                         strap_mm: nil,
                         top_cheek_mm: nil,
                         mid_cheek_mm: nil,
                         chin_mm: nil
                       }
                     end
                   else
                     {
                       nose_mm: nil,
                       strap_mm: nil,
                       top_cheek_mm: nil,
                       mid_cheek_mm: nil,
                       chin_mm: nil
                     }
                   end

      # Convert symbol keys to string keys to match SQL result format
      aggregated_string_keys = aggregated.transform_keys(&:to_s)
      row.merge(aggregated_string_keys)
    end

    # Compute stats on aggregated measurements
    stats = FacialMeasurementOutliersService.compute_aggregated_stats(facial_measurements_with_aggregated)

    # Add z-scores for each row and remove arkit key
    facial_measurements_with_aggregated.map do |row|
      z_scores = FacialMeasurementOutliersService.compute_z_scores(row, stats)
      row.merge(z_scores).except('arkit', 'facial_measurement_id')
    end
  end
end
