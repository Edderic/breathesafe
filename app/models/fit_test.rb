class FitTest < ApplicationRecord
  belongs_to :mask, optional: true
  belongs_to :facial_measurement, optional: true
  belongs_to :user

  def self.viewable(user)
    fit_tests = FitTest.connection.exec_query(
      <<-SQL
        SELECT ft.*, m.id as mask_id, m.unique_internal_model_code, m.image_urls, m.has_exhalation_valve, m.strap_type, m.perimeter_mm, fm.user_id AS fm_user_id, p.first_name, p.last_name,
          #{self.facial_measurement_presence}

        FROM fit_tests ft
        LEFT JOIN facial_measurements fm
        ON (fm.id = ft.facial_measurement_id)
        LEFT JOIN profiles p
        ON (p.user_id = ft.user_id)
        LEFT JOIN masks m
        ON (m.id = ft.mask_id)
        WHERE ft.user_id IN (
          SELECT mu.managed_id
          FROM managed_users mu
          WHERE mu.manager_id = '#{user.id}'
        )

        ORDER BY updated_at DESC
      SQL
    )

    self.json_parse(fit_tests, ["facial_hair", "comfort", "results", "user_seal_check", "image_urls"])
  end

  def self.find_by_id_with_user_id(id)
    fit_tests = FitTest.connection.exec_query(
      <<-SQL
        SELECT ft.*, m.unique_internal_model_code, m.image_urls, m.has_exhalation_valve, fm.user_id, p.first_name, p.last_name,
        #{self.facial_measurement_presence}

        FROM fit_tests ft
        LEFT JOIN facial_measurements fm
        ON (fm.id = ft.facial_measurement_id)
        LEFT JOIN profiles p
        ON (p.user_id = ft.user_id)
        LEFT JOIN masks m
        ON (m.id = ft.mask_id)
        WHERE ft.id = '#{id}'

        ORDER BY updated_at DESC
      SQL
    )

    self.json_parse(fit_tests, ["facial_hair", "comfort", "results", "user_seal_check", "image_urls"])[0]
  end

  def self.json_parse(events, columns)
    events.map do |ev|
      columns.each do |col|
        if !ev[col]
          ev[col] = []
        elsif col == "image_urls"
          ev[col] = [ev['image_urls'].gsub("{","").gsub("}","").gsub('"', '')]
        else
          ev[col] = JSON.parse(ev[col])
        end
      end

      ev
    end
  end

  def self.facial_measurement_presence
    <<-SQL
      CASE WHEN fm.face_width IS NOT NULL
          AND fm.jaw_width IS NOT NULL
          AND fm.face_depth IS NOT NULL
          AND fm.face_length IS NOT NULL
          AND fm.lower_face_length IS NOT NULL
          AND fm.bitragion_menton_arc IS NOT NULL
          AND fm.bitragion_subnasale_arc IS NOT NULL
          AND fm.cheek_fullness IS NOT NULL
          AND fm.nasal_root_breadth IS NOT NULL
          AND fm.nose_protrusion IS NOT NULL
          AND fm.nose_bridge_height IS NOT NULL
          AND fm.lip_width IS NOT NULL
        THEN 'Complete'
      WHEN fm.id IS NULL
        THEN 'Completely missing'
      ELSE 'Partially missing'
      END AS facial_measurement_presence
    SQL
  end
end
