# frozen_string_literal: true

# Service to compute database-wide ranges for mask stats.
class MasksDataContextualizer
  class << self
    def call
      stats = Mask.connection.exec_query(<<-SQL).first || {}
        WITH fit_test_counts_per_mask AS (
          SELECT m.id as mask_id, COUNT(ft.id) AS fit_test_count
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id
        ),
        breathability_measurements AS (
          SELECT m.id, b ->> 'breathability_pascals' as breathability_pascals
          FROM masks m, jsonb_array_elements(
                CASE
                  WHEN jsonb_typeof(breathability) = 'array' THEN breathability
                  ELSE jsonb_build_array(breathability)
                END
          ) AS b
        ),
        breathability_aggregates AS (
          SELECT id,
            AVG(CASE
              WHEN breathability_pascals ~ '^[0-9]+\\.?[0-9]*$'
              THEN breathability_pascals::numeric
              ELSE NULL
            END) AS avg_breathability_pa
          FROM breathability_measurements
          GROUP BY 1
        )
        SELECT
          MIN(masks.perimeter_mm) AS perimeter_min,
          MAX(masks.perimeter_mm) AS perimeter_max,
          MIN(breathability_aggregates.avg_breathability_pa) AS breathability_min,
          MAX(breathability_aggregates.avg_breathability_pa) AS breathability_max,
          MAX(COALESCE(fit_test_counts_per_mask.fit_test_count, 0)) AS fit_test_count_max
        FROM masks
        LEFT JOIN fit_test_counts_per_mask ON fit_test_counts_per_mask.mask_id = masks.id
        LEFT JOIN breathability_aggregates ON breathability_aggregates.id = masks.id
      SQL

      {
        breathability_min: to_float(stats['breathability_min']),
        breathability_max: to_float(stats['breathability_max']),
        perimeter_min: to_float(stats['perimeter_min']),
        perimeter_max: to_float(stats['perimeter_max']),
        fit_test_count_max: to_integer(stats['fit_test_count_max'])
      }
    end

    private

    def to_float(value)
      value.nil? ? nil : value.to_f
    end

    def to_integer(value)
      value.nil? ? nil : value.to_i
    end
  end
end
