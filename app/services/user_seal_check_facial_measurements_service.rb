class UserSealCheckFacialMeasurementsService
  class << self
    def call(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id}" : ""

      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH fit_tests_with_seal_checks AS (
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
            (facial_hair ->> 'beard_length_mm')::integer as facial_hair_beard_length_mm,
            #{FacialMeasurement::COLUMNS.join(', ')},
            '#{self}' AS source
          FROM fit_tests_with_seal_checks
          INNER JOIN fit_tests ON fit_tests.id = fit_tests_with_seal_checks.id
          LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
        SQL
      )
    end
  end
end
