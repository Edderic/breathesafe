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

      manager_select = manager_id ? 'manager.email as manager_email' : 'NULL as manager_email'
      zscore_select = zscore_cols.to_s.strip
      zscore_select = zscore_select.empty? ? '' : ",\n            #{zscore_select}"

      <<-SQL
        zscored_sql AS (
          SELECT
            fm.id,
            fm.user_id,
            u.email as user_email,
            p.first_name,
            p.last_name,
            (p.first_name || ' ' || p.last_name) as full_name,
            #{manager_select}#{zscore_select}
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
      normalize_value = lambda do |value|
        return nil if value.nil?

        value = value.presence if value.respond_to?(:presence)
        return nil if value.nil?

        numeric = value.to_f
        numeric.zero? ? nil : numeric
      end

      scope = FacialMeasurement.all
      manager_email = nil
      if manager_id
        managed_user_ids = ManagedUser.where(manager_id: manager_id).pluck(:managed_id)
        return [] if managed_user_ids.empty?

        scope = scope.where(user_id: managed_user_ids)
        manager_email = User.find_by(id: manager_id)&.email
      end

      measurements = scope.to_a
      latest_measurements = measurements.group_by(&:user_id).values.map do |rows|
        rows.max_by { |row| [row.created_at || Time.zone.at(0), row.id] }
      end

      lower_bound = facial_measurement_id_of_lower_bound &&
                    FacialMeasurement.find_by(id: facial_measurement_id_of_lower_bound)
      upper_bound = facial_measurement_id_of_upper_bound &&
                    FacialMeasurement.find_by(id: facial_measurement_id_of_upper_bound)

      if lower_bound || upper_bound
        latest_measurements.select! do |measurement|
          bound_columns = FacialMeasurement::COLUMNS - %w[head_circumference nose_breadth]
          bound_columns.all? do |column|
            value_num = normalize_value.call(measurement.public_send(column))
            lower_num = normalize_value.call(lower_bound&.public_send(column))
            upper_num = normalize_value.call(upper_bound&.public_send(column))

            (lower_num.nil? || value_num.nil? || value_num >= lower_num) &&
              (upper_num.nil? || value_num.nil? || value_num <= upper_num)
          end
        end
      end

      stats = FacialMeasurement::COLUMNS.index_with do |column|
        values = latest_measurements.map do |measurement|
          normalize_value.call(measurement.public_send(column)) || 0.0
        end
        if values.empty?
          { mean: nil, std: nil }
        else
          mean = values.sum / values.length
          e_of_x_squared = values.sum { |value| value**2 } / values.length
          std = Math.sqrt(e_of_x_squared - mean**2)
          { mean: mean, std: std }
        end
      end

      user_ids = latest_measurements.map(&:user_id)
      users_by_id = User.where(id: user_ids).index_by(&:id)
      profiles_by_user_id = Profile.where(user_id: user_ids).index_by(&:user_id)

      rows = latest_measurements.map do |measurement|
        user = users_by_id[measurement.user_id]
        profile = profiles_by_user_id[measurement.user_id]
        full_name = [profile&.first_name, profile&.last_name].compact.join(' ')

        row = {
          'id' => measurement.id,
          'user_id' => measurement.user_id,
          'user_email' => user&.email,
          'first_name' => profile&.first_name,
          'last_name' => profile&.last_name,
          'full_name' => full_name,
          'manager_email' => manager_email
        }

        FacialMeasurement::COLUMNS.each do |column|
          raw_value = measurement.public_send(column)
          value_num = normalize_value.call(raw_value)
          row[column] = raw_value.presence

          mean = stats[column][:mean]
          std = stats[column][:std]
          row["#{column}_z_score"] = if value_num.nil? || mean.nil? || std.nil? || std.zero?
                                       nil
                                     else
                                       (value_num - mean) / std
                                     end
        end

        row
      end

      rows.sort_by { |row| [row['last_name'].to_s, row['first_name'].to_s] }
    end
  end
end
