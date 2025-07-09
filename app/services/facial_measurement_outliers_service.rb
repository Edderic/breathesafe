class FacialMeasurementOutliersService
  class << self
    def avg_stddev_cols
      FacialMeasurement::COLUMNS.map do |col|
        <<-SQL
        AVG(#{col}) AS avg_#{col},
        STDDEV_POP(#{col}) stddev_#{col}
        SQL
      end.join(",")
    end

    def zscore_cols
      FacialMeasurement::COLUMNS.map do |col|
        <<-SQL
          CASE
            WHEN fm.#{col} IS NULL THEN NULL
            WHEN ms.stddev_#{col} = 0 THEN NULL
            ELSE (fm.#{col} - ms.avg_#{col}) / ms.stddev_#{col}
          END as #{col}_z_score
        SQL
      end.join(",")
    end

    def dedup_sql
      # Represent a user only once
      <<-SQL
      facial_measurements_deduped AS (
        SELECT * FROM facial_measurements fm
      )
      SQL
    end

    def measurement_stats_sql
      <<-SQL
        measurement_stats AS (
          SELECT
            1
            id,
            #{avg_stddev_cols}
          FROM facial_measurements_deduped fm
          GROUP BY 1
        )
      SQL
    end

    def call
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH
        #{dedup_sql},
        #{measurement_stats_sql}

        SELECT
          fm.id,
          fm.user_id,
          u.email as user_email,
          p.first_name,
          p.last_name,
          (p.first_name || ' ' || p.last_name) as full_name,
          manager.email as manager_email,
          #{zscore_cols},
          #{FacialMeasurement::COLUMNS.join(', ')}
        FROM facial_measurements fm
        INNER JOIN users u ON u.id = fm.user_id
        INNER JOIN profiles p ON p.user_id = fm.user_id
        INNER JOIN managed_users mu ON mu.managed_id = fm.user_id
        INNER JOIN users manager ON manager.id = mu.manager_id
        CROSS JOIN measurement_stats ms
        WHERE fm.id IN (
          SELECT MAX(fm2.id)
          FROM facial_measurements fm2
          GROUP BY fm2.user_id
        )
        ORDER BY p.last_name, p.first_name
        SQL
      )
    end
  end
end
