# frozen_string_literal: true

class UserSealCheckFacialMeasurementsService
  class << self
    # When user seal check hash is present, and (sizing is too big or too small)
    # OR user notes that there is "a lot of air movement", then it's a failure
    # otherwise, we are unsure -- need to do a quantitative or qualitative fit
    # test
    def call(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ''

      results = ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH
          #{FacialMeasurementOutliersService.latest_measurements_sql},
          #{FacialMeasurementOutliersService.measurement_stats_sql_without_bounds},
          fit_tests_with_seal_checks AS (
            SELECT id,
              mask_id,
              user_seal_check,
              -- Use UserSealCheckService logic to determine qlft_pass
              -- This will be computed in Ruby after fetching results
              NULL as qlft_pass
            FROM fit_tests
            WHERE user_seal_check IS NOT NULL
            #{mask_id_clause}
          )

          SELECT fit_tests_with_seal_checks.*,
            (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
            masks.unique_internal_model_code,
            masks.perimeter_mm,
            masks.strap_type,
            masks.style,
            '#{self}' AS source,
            fit_tests.user_id,
            fit_tests.created_at,
            fit_tests.facial_measurement_id,
            facial_measurements.arkit
          FROM fit_tests_with_seal_checks
          INNER JOIN fit_tests ON fit_tests.id = fit_tests_with_seal_checks.id
          INNER JOIN masks ON fit_tests.mask_id = masks.id
          LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
        SQL
      )

      # Compute qlft_pass and aggregated ARKit measurements in Ruby
      facial_measurements_with_aggregated = results.map do |row|
        # Set qlft_pass based on user seal check evaluation
        user_seal_check_data = row['user_seal_check']
        row['qlft_pass'] = UserSealCheckService.qlft_pass_value(user_seal_check_data)
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
end
