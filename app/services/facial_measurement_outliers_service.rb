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
        WHERE id IN (
          SELECT facial_measurement_id
          FROM fit_tests
        )
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
          #{zscore_cols}
        FROM facial_measurements fm
        CROSS JOIN measurement_stats ms
        SQL
      )
    end
  end
end
