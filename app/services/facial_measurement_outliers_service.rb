# frozen_string_literal: true

class FacialMeasurementOutliersService
  # Aggregated ARKit measurement columns
  AGGREGATED_COLUMNS = %w[nose_mm strap_mm top_cheek_mm mid_cheek_mm chin_mm].freeze

  class << self
    def measurement_stats_sql_without_bounds
      # This method is kept for backward compatibility but now returns empty SQL
      # Stats are computed in Ruby after fetching aggregated measurements
      <<-SQL
        measurement_stats AS (
          SELECT 1 as id
        )
      SQL
    end

    def compute_aggregated_stats(facial_measurements)
      # Compute stats on aggregated ARKit measurements in Ruby
      stats = {}

      AGGREGATED_COLUMNS.each do |col|
        values = facial_measurements.map { |fm| fm[col] }.compact

        if values.any?
          avg = values.sum.to_f / values.length
          variance = values.sum { |v| (v - avg)**2 } / values.length
          stddev = Math.sqrt(variance)

          stats["avg_#{col}"] = avg
          stats["stddev_#{col}"] = stddev
        else
          stats["avg_#{col}"] = nil
          stats["stddev_#{col}"] = nil
        end
      end

      stats
    end

    def compute_z_scores(facial_measurement, stats)
      # Compute z-scores for aggregated measurements
      z_scores = {}

      AGGREGATED_COLUMNS.each do |col|
        value = facial_measurement[col]
        avg = stats["avg_#{col}"]
        stddev = stats["stddev_#{col}"]

        z_scores["#{col}_z_score"] = if value.nil? || avg.nil? || stddev.nil? || stddev.zero?
                                       nil
                                     else
                                       (value - avg) / stddev
                                     end
      end

      z_scores
    end

    def zscore_cols
      # Deprecated: kept for backward compatibility
      # Z-scores are now computed in Ruby
      ''
    end

    def latest_measurements_sql
      <<-SQL
        latest_facial_measurements AS (
          SELECT DISTINCT ON (user_id) *
          FROM facial_measurements
          ORDER BY user_id, created_at DESC
        )
      SQL
    end

    def measurement_stats_sql(manager_id: nil, lower_bound_id: nil, upper_bound_id: nil)
      manager_sql = <<-SQL
        INNER JOIN managed_users mu ON mu.managed_id = fm.user_id AND mu.manager_id = #{manager_id}
      SQL

      manager_filter = manager_id ? manager_sql : ''

      lower_bound_join = lower_bound_id ? "LEFT JOIN facial_measurements lb ON lb.id = #{lower_bound_id}" : ''
      upper_bound_join = upper_bound_id ? "LEFT JOIN facial_measurements ub ON ub.id = #{upper_bound_id}" : ''

      <<-SQL
        measurement_stats AS (
          SELECT
            1 as id
          FROM latest_facial_measurements fm
          #{lower_bound_join}
          #{upper_bound_join}
          #{manager_filter}
        )
      SQL
    end

    def zscored_sql(manager_id: nil, facial_measurement_id_of_lower_bound: nil,
                    facial_measurement_id_of_upper_bound: nil)
      manager_filter = ''
      if manager_id
        manager_filter = <<-SQL
          INNER JOIN managed_users mu ON mu.managed_id = fm.user_id AND mu.manager_id = #{manager_id}
        SQL
      end

      lower_bound_join = ''
      if facial_measurement_id_of_lower_bound
        lower_bound_join = <<-SQL
          LEFT JOIN facial_measurements lb ON lb.id = #{facial_measurement_id_of_lower_bound}
        SQL
      end
      upper_bound_join = ''
      if facial_measurement_id_of_upper_bound
        upper_bound_join = <<-SQL
          LEFT JOIN facial_measurements ub ON ub.id = #{facial_measurement_id_of_upper_bound}
        SQL
      end

      <<-SQL
        zscored_sql AS (
          SELECT
            fm.id,
            fm.user_id,
            u.email as user_email,
            p.first_name,
            p.last_name,
            (p.first_name || ' ' || p.last_name) as full_name,
            #{manager_id ? 'manager.email as manager_email,' : 'NULL as manager_email,'}
            #{zscore_cols},
          FROM latest_facial_measurements fm
          INNER JOIN users u ON u.id = fm.user_id
          INNER JOIN profiles p ON p.user_id = fm.user_id
          #{manager_id ? "INNER JOIN users manager ON manager.id = #{manager_id}" : ''}
          #{lower_bound_join}
          #{upper_bound_join}
          #{manager_filter}
          CROSS JOIN measurement_stats ms
          ORDER BY p.last_name, p.first_name
        )
      SQL
    end

    def call(manager_id: nil, facial_measurement_id_of_lower_bound: nil, facial_measurement_id_of_upper_bound: nil)
      sql = <<-SQL
        WITH
        #{latest_measurements_sql},
        #{measurement_stats_sql(manager_id: manager_id, lower_bound_id: facial_measurement_id_of_lower_bound, upper_bound_id: facial_measurement_id_of_upper_bound)},
        #{zscored_sql(manager_id:, facial_measurement_id_of_lower_bound:, facial_measurement_id_of_upper_bound:)}

        SELECT * FROM zscored_sql
      SQL

      ActiveRecord::Base.connection.exec_query(sql)
    end
  end
end
