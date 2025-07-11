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
      latest_facial_measurement_ids AS (
        SELECT user_id, MAX(id) AS id FROM facial_measurements fm
        GROUP BY 1
      ),
      latest_facial_measurements_per_user AS (
        SELECT * FROM facial_measurements fm
        WHERE id in (
          SELECT id FROM latest_facial_measurement_ids
        )
      )

      SQL
    end

    def measurement_stats_sql(manager_id: nil)
      # Calculate stats from measurements that have fit tests, matching get_zscores function
      # Use DISTINCT to avoid counting the same measurement multiple times
      <<-SQL
        measurement_stats AS (
          SELECT
            1
            id,
            #{avg_stddev_cols}
          FROM (
            SELECT DISTINCT fm.id, fm.face_width, fm.jaw_width, fm.face_depth, fm.face_length,
                   fm.lower_face_length, fm.bitragion_menton_arc, fm.bitragion_subnasale_arc,
                   fm.nasal_root_breadth, fm.nose_protrusion, fm.nose_bridge_height,
                   fm.lip_width, fm.head_circumference, fm.nose_breadth
            FROM latest_facial_measurements_per_user fm
            INNER JOIN fit_tests ft ON ft.user_id = fm.user_id
          ) fm_distinct
          GROUP BY 1
        )
      SQL
    end

    def call(manager_id: nil)
      manager_filter = manager_id ? "INNER JOIN managed_users mu ON mu.managed_id = fm.user_id AND mu.manager_id = #{manager_id}" : ""

      # Debug: Check what measurements are being used for stats
      stats_query = <<-SQL
        SELECT COUNT(*) as count, AVG(face_width) as avg_face_width, STDDEV_POP(face_width) as stddev_face_width
        FROM facial_measurements fm
        INNER JOIN fit_tests ft ON ft.facial_measurement_id = fm.id
      SQL

      # Debug: Show specific measurements used in service stats
      specific_stats_query = <<-SQL
        SELECT fm.id, fm.user_id, fm.face_width
        FROM facial_measurements fm
        INNER JOIN fit_tests ft ON ft.facial_measurement_id = fm.id
        ORDER BY fm.id
      SQL
      specific_stats = ActiveRecord::Base.connection.exec_query(specific_stats_query).to_a
      puts "Service stats measurements:"
      specific_stats.each do |m|
        puts "  ID: #{m['id']}, User: #{m['user_id']}, face_width: #{m['face_width']}"
      end

      sql = <<-SQL
        WITH
        #{dedup_sql},
        #{measurement_stats_sql(manager_id: manager_id)}

        SELECT
          fm.id,
          fm.user_id,
          u.email as user_email,
          p.first_name,
          p.last_name,
          (p.first_name || ' ' || p.last_name) as full_name,
          #{manager_id ? "manager.email as manager_email," : "NULL as manager_email,"}
          #{zscore_cols},
          #{FacialMeasurement::COLUMNS.join(', ')}
        FROM latest_facial_measurements_per_user fm
        INNER JOIN users u ON u.id = fm.user_id
        INNER JOIN profiles p ON p.user_id = fm.user_id
        #{manager_id ? "INNER JOIN users manager ON manager.id = #{manager_id}" : ""}
        #{manager_filter}
        CROSS JOIN measurement_stats ms
        ORDER BY p.last_name, p.first_name
        SQL

      result = ActiveRecord::Base.connection.exec_query(sql)
      result
    end
  end
end
