class UserSealCheckFacialMeasurementsService
  class << self
    def call(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ""

      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH
          #{FacialMeasurementOutliersService.latest_measurements_sql},
          #{FacialMeasurementOutliersService.measurement_stats_sql_without_bounds},
          fit_tests_with_seal_checks AS (
            SELECT id,
              mask_id,
              user_seal_check,
              CASE
                WHEN user_seal_check -> 'sizing' ->> 'What do you think about the sizing of this mask relative to your face?' IN ('Too small', 'Too big')
                  THEN false
                WHEN user_seal_check -> 'positive' ->> '...how much air movement on your face along the seal of the mask did you feel?' = 'A lot of air movement'
                  THEN false
                ELSE NULL
              END as qlft_pass
            FROM fit_tests
            WHERE user_seal_check IS NOT NULL
            #{mask_id_clause}
          )

          SELECT fit_tests_with_seal_checks.*,
            (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
            #{FacialMeasurement::COLUMNS.join(', ')},
            #{FacialMeasurement::COLUMNS.map do |col|
              <<-SQL
                CASE
                  WHEN facial_measurements.#{col} IS NULL THEN NULL
                  WHEN ms.stddev_#{col} = 0 OR ms.stddev_#{col} IS NULL THEN NULL
                  ELSE (facial_measurements.#{col} - ms.avg_#{col}) / ms.stddev_#{col}
                END as #{col}_z_score
              SQL
            end.join(',')},
            '#{self}' AS source,
            fit_tests.user_id
          FROM fit_tests_with_seal_checks
          INNER JOIN fit_tests ON fit_tests.id = fit_tests_with_seal_checks.id
          LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
          CROSS JOIN measurement_stats ms
        SQL
      )
    end
  end
end
