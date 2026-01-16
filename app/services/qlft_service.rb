# frozen_string_literal: true

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
    def call(mask_id: nil)
      mask_id_clause = mask_id ? "AND mask_id = #{mask_id.to_i}" : ''

      results = ActiveRecord::Base.connection.exec_query(
        <<-SQL
          WITH #{FacialMeasurementOutliersService.latest_measurements_sql},
          #{FacialMeasurementOutliersService.measurement_stats_sql_without_bounds},
          qlft_exercises AS (
            SELECT * FROM fit_tests
            WHERE results -> 'qualitative' IS NOT NULL
            #{mask_id_clause}
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
            fit_tests.user_seal_check::jsonb AS user_seal_check,
            (regexp_replace(facial_hair ->> 'beard_length_mm', '[^0-9]', '', 'g'))::integer as facial_hair_beard_length_mm,
            explicit_pass_count as n,
            NULL as denominator,
            NULL as n95_mode_hmff,
            masks.unique_internal_model_code,
            masks.perimeter_mm,
            masks.strap_type,
            masks.style,
            '#{self}' AS source,
            fit_tests.user_id,
            fit_tests.mask_modded,
            fit_tests.created_at,
            mask_id,
            fit_tests.facial_measurement_id
          FROM qlft_pass_status_maybe_null
          INNER JOIN fit_tests ON fit_tests.id = qlft_pass_status_maybe_null.id
          INNER JOIN masks ON fit_tests.mask_id = masks.id
        SQL
      )

      # Load FacialMeasurements through ActiveRecord to get decrypted data
      # Group results by facial_measurement_id to batch load
      fm_ids = results.map { |row| row['facial_measurement_id'] }.compact.uniq
      facial_measurements_by_id = FacialMeasurement.where(id: fm_ids).index_by(&:id)

      # Compute aggregated ARKit measurements in Ruby
      facial_measurements_with_aggregated = results.map do |row|
        facial_measurement_id = row['facial_measurement_id']

        measurement_data = if facial_measurement_id
                             fm = facial_measurements_by_id[facial_measurement_id]
                             if fm
                               FacialMeasurement::COLUMNS.index_with { |column| fm.public_send(column) }
                             else
                               {}
                             end
                           else
                             {}
                           end

        aggregated = if facial_measurement_id
                       fm = facial_measurements_by_id[facial_measurement_id]
                       if fm && fm.arkit.present?
                         begin
                           fm.aggregated_arkit_measurements
                         rescue StandardError => e
                           Rails.logger.error(
                             "Error computing aggregated measurements for FM #{facial_measurement_id}: #{e.message}"
                           )
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
        row.merge(aggregated_string_keys).merge(measurement_data)
      end

      # Compute stats on aggregated measurements
      stats = FacialMeasurementOutliersService.compute_aggregated_stats(facial_measurements_with_aggregated)
      standard_stats = compute_standard_stats(facial_measurements_with_aggregated)

      # Add z-scores for each row and remove arkit key
      facial_measurements_with_aggregated.map do |row|
        z_scores = FacialMeasurementOutliersService.compute_z_scores(row, stats)
        standard_z_scores = compute_standard_z_scores(row, standard_stats)
        row.merge(z_scores).merge(standard_z_scores).except('arkit')
      end
    end

    def compute_standard_stats(rows)
      FacialMeasurement::COLUMNS.index_with do |column|
        values = rows.map { |row| row[column] }.compact.map(&:to_f)
        if values.empty?
          { mean: nil, std: nil }
        else
          mean = values.sum / values.length
          variance = values.sum { |value| (value - mean)**2 } / values.length
          { mean: mean, std: Math.sqrt(variance) }
        end
      end
    end

    def compute_standard_z_scores(row, stats)
      stats.each_with_object({}) do |(column, stat), accum|
        value = row[column]
        accum["#{column}_z_score"] = if value.nil? || stat[:mean].nil? || stat[:std].nil? || stat[:std].zero?
                                       nil
                                     else
                                       (value.to_f - stat[:mean]) / stat[:std]
                                     end
      end
    end

    private :compute_standard_stats, :compute_standard_z_scores
  end
end
