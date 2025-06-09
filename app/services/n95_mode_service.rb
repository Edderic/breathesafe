class N95ModeService
  def self.call
    # Looks for FitTests where testing_mode is 'N95'
    # Computes the harmonic mean fit factor (hmff) for all the exercises,
    # with the exception of Normal breathing (SEALED)
    ActiveRecord::Base.connection.exec_query(
      <<-SQL

        WITH n95_exercises AS (
            SELECT * FROM fit_tests
            WHERE results -> 'quantitative' ->> 'testing_mode' = 'N95'
        ), n95_exercise_name_and_fit_factors AS (
            SELECT n95_exercises.id,
            mask_id,
            exercises ->> 'name' AS exercise_name,
            (exercises ->> 'fit_factor')::numeric as exercise_fit_factor,
            CASE WHEN (exercises ->> 'fit_factor')::numeric IS NULL THEN NULL
              ELSE 1 / (exercises ->> 'fit_factor')::numeric END AS inverse_exercise_fit_factor
            FROM n95_exercises, jsonb_array_elements(results -> 'quantitative' -> 'exercises') as exercises
            WHERE exercises ->> 'name' != 'Normal breathing (SEALED)'
        )
        SELECT id,
          COUNT(*) as n,
          SUM(inverse_exercise_fit_factor) as denominator,
          COUNT(*) / SUM(inverse_exercise_fit_factor) as n95_mode_hmff,
          COUNT(*) / SUM(inverse_exercise_fit_factor) >= 100 AS qlft_pass
        FROM n95_exercise_name_and_fit_factors
        GROUP BY 1
      SQL
    )
  end
end
