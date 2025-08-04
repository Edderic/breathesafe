# frozen_string_literal: true

class FacialMeasurementOutliersService
  class << self
    def measurement_stats_sql_without_bounds
      <<-SQL
        measurement_stats AS (
          SELECT
            1 as id,
            #{FacialMeasurement::COLUMNS.map do |col|
              <<-SQL
                AVG(fm.#{col}) AS avg_#{col},
                STDDEV_POP(fm.#{col}) AS stddev_#{col}
              SQL
            end.join(',')}
          FROM latest_facial_measurements fm
        )
      SQL
    end

    def avg_stddev_cols(lower_bound_id: nil, upper_bound_id: nil)
      FacialMeasurement::COLUMNS.map do |col|
        bounds_conditions = []

        bounds_conditions << "fm.#{col} >= lb.#{col}" if lower_bound_id

        bounds_conditions << "fm.#{col} <= ub.#{col}" if upper_bound_id

        if bounds_conditions.any?
          <<-SQL
          AVG(CASE WHEN #{bounds_conditions.join(' AND ')} THEN fm.#{col} ELSE NULL END) AS avg_#{col},
          STDDEV_POP(CASE WHEN #{bounds_conditions.join(' AND ')} THEN fm.#{col} ELSE NULL END) AS stddev_#{col}
          SQL
        else
          <<-SQL
          AVG(fm.#{col}) AS avg_#{col},
          STDDEV_POP(fm.#{col}) AS stddev_#{col}
          SQL
        end
      end.join(',')
    end

    def zscore_cols
      FacialMeasurement::COLUMNS.map do |col|
        <<-SQL
          CASE
            WHEN fm.#{col} IS NULL THEN NULL
            WHEN ms.stddev_#{col} = 0 OR ms.stddev_#{col} IS NULL THEN NULL
            ELSE (fm.#{col} - ms.avg_#{col}) / ms.stddev_#{col}
          END as #{col}_z_score
        SQL
      end.join(',')
    end

    def bounds_filter_cols(lower_bound_id: nil, upper_bound_id: nil)
      if lower_bound_id.nil? && upper_bound_id.nil?
        return FacialMeasurement::COLUMNS.map do |col|
          "fm.#{col}"
        end.join(', ')
      end

      FacialMeasurement::COLUMNS.map do |col|
        conditions = []

        conditions << "fm.#{col} >= lb.#{col}" if lower_bound_id

        conditions << "fm.#{col} <= ub.#{col}" if upper_bound_id

        if conditions.any?
          <<-SQL
            CASE
              WHEN #{conditions.join(' AND ')} THEN fm.#{col}
              ELSE NULL
            END as #{col}
          SQL
        else
          "fm.#{col}"
        end
      end.join(', ')
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
        INNER JOIN managed_users mu ON mu.managed_id = fm.user_id AND mu.manager_id = #{manager_id}"
      SQL

      manager_filter = manager_id ? manager_sql : ''

      lower_bound_join = lower_bound_id ? "LEFT JOIN facial_measurements lb ON lb.id = #{lower_bound_id}" : ''
      upper_bound_join = upper_bound_id ? "LEFT JOIN facial_measurements ub ON ub.id = #{upper_bound_id}" : ''

      <<-SQL
        measurement_stats AS (
          SELECT
            1 as id,
            #{avg_stddev_cols(lower_bound_id: lower_bound_id, upper_bound_id: upper_bound_id)}
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
            #{bounds_filter_cols(lower_bound_id: facial_measurement_id_of_lower_bound, upper_bound_id: facial_measurement_id_of_upper_bound)}
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
