class QlftService
  class << self
    # Returns qualitative fit testing data, with facial measurements if
    # available.
    #
    # Returns: list[hash]
    # Each hash has at least the following keys:
    #   qlft_pass: boolean.
    #     Whether or not the qualitative fit test passed. A qualitative fit
    #     test passed if all the exercises' fit factors that are non-null /
    #     non-blank say "Pass" and there is at least one that is a "Pass".
    #     Traditionally, a qualitative fit test passes when ALL exercises
    #     "Pass", but I'm being more lenient here to be more inclusive of
    #     kids, who are harder to test than adults.
    #
    #   n: integer or nil.
    #     Always returns a nil, for compatibility with quantitative fit testing
    #     results
    #
    #   denominator: integer or nil.
    #     Always returns a nil, for compatibility with quantitative fit testing
    #     results
    #
    #   n95_mode_hmff: integer or nil.
    #     Always returns a nil, for compatibility with quantitative fit testing
    #     results
    #
    def call
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH qlft_exercises AS (
            SELECT * FROM fit_tests
            WHERE results -> 'qualitative' IS NOT NULL
          ), qlft_exercise_results AS (
            SELECT qlft_exercises.id,
              exercises ->> 'name' AS exercise_name,
              exercises ->> 'result' AS exercise_result
            FROM qlft_exercises, jsonb_array_elements(results -> 'qualitative' -> 'exercises') as exercises
          ), qlft_pass_status AS (
            SELECT id,
              SUM(
                CASE WHEN exercise_result = 'Pass' THEN 1 ELSE 0 END
              ) AS explicit_pass_count,
              BOOL_AND(
                CASE
                  WHEN exercise_result IS NULL OR exercise_result = '' THEN true
                  ELSE exercise_result = 'Pass'
                END
              ) AS qlft_pass
            FROM qlft_exercise_results
            GROUP BY 1
          ), qlft_pass_status_maybe_null AS (
            SELECT id,
            explicit_pass_count,
            CASE WHEN explicit_pass_count < 1 THEN NULL ELSE qlft_pass END as qlft_pass
            FROM qlft_pass_status
          )


          SELECT qlft_pass_status_maybe_null.*,
            (facial_hair ->> 'beard_length_mm')::integer as facial_hair_beard_length_mm,
            explicit_pass_count as n,
            NULL as denominator,
            NULL as n95_mode_hmff,
            #{FacialMeasurement::COLUMNS.join(', ')}
          FROM qlft_pass_status_maybe_null
          INNER JOIN fit_tests ON fit_tests.id = qlft_pass_status_maybe_null.id
          LEFT JOIN facial_measurements ON fit_tests.facial_measurement_id = facial_measurements.id
        SQL
      )
    end
  end
end
