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
              WHEN exercises ->> 'fit_factor' IS NULL THEN NULL
              WHEN LOWER(exercises ->> 'fit_factor') = 'aborted' THEN NULL
              WHEN exercises ->> 'fit_factor' ~ '^[0-9]+\.?[0-9]*$' THEN (exercises ->> 'fit_factor')::numeric
              ELSE NULL
            END as exercise_fit_factor,
            CASE#{' '}
              WHEN exercises ->> 'fit_factor' = '' THEN NULL
              WHEN exercises ->> 'fit_factor' IS NULL THEN NULL
              WHEN LOWER(exercises ->> 'fit_factor') = 'aborted' THEN NULL
              WHEN exercises ->> 'fit_factor' ~ '^[0-9]+\.?[0-9]*$' THEN 1 / (exercises ->> 'fit_factor')::numeric
              ELSE NULL
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
          fit_tests.mask_modded,
          fit_tests.created_at,
          masks.unique_internal_model_code,
          masks.perimeter_mm,
          masks.strap_type,
          masks.style,
          fit_tests.facial_measurement_id
        FROM n95_mode_experimentals
        INNER JOIN fit_tests ON fit_tests.id = n95_mode_experimentals.id
        INNER JOIN masks ON fit_tests.mask_id = masks.id
      SQL
    )

    # Load FacialMeasurements through ActiveRecord to get decrypted data
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

  def self.compute_standard_stats(rows)
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

  def self.compute_standard_z_scores(row, stats)
    stats.each_with_object({}) do |(column, stat), accum|
      value = row[column]
      accum["#{column}_z_score"] = if value.nil? || stat[:mean].nil? || stat[:std].nil? || stat[:std].zero?
                                     nil
                                   else
                                     (value.to_f - stat[:mean]) / stat[:std]
                                   end
    end
  end

  private_class_method :compute_standard_stats, :compute_standard_z_scores
end
