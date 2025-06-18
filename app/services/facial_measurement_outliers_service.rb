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

    def call
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH measurement_stats AS (
          SELECT
            1
            id,
            #{avg_stddev_cols}
          FROM facial_measurements fm
          INNER JOIN fit_tests ft on ft.facial_measurement_id = fm.id
          GROUP BY 1
        )
        SELECT
          fm.id,
          fm.user_id,
          fm.face_width,
          #{zscore_cols}
        FROM facial_measurements fm
        CROSS JOIN measurement_stats ms
        SQL
      )
    end
  end
end
