class FitTest < ApplicationRecord
  belongs_to :mask, optional: true
  belongs_to :facial_measurement

  def self.viewable(user)

    fit_tests = FitTest.connection.exec_query(
      <<-SQL
        SELECT ft.*, m.unique_internal_model_code, m.image_urls, m.has_exhalation_valve, fm.user_id
        FROM fit_tests ft
        INNER JOIN facial_measurements fm
        ON (fm.id = ft.facial_measurement_id)
        LEFT JOIN masks m
        ON (m.id = ft.mask_id)
        WHERE fm.user_id IN (
          SELECT mu.managed_id
          FROM managed_users mu
          WHERE mu.manager_id = '#{user.id}'
        )

        ORDER BY updated_at DESC
      SQL
    )

    self.json_parse(fit_tests, ["comfort", "results", "user_seal_check", "image_urls"])
  end

  def self.find_by_id_with_user_id(id)
    fit_tests = FitTest.connection.exec_query(
      <<-SQL
        SELECT ft.*, m.unique_internal_model_code, m.image_urls, m.has_exhalation_valve, fm.user_id
        FROM fit_tests ft
        INNER JOIN facial_measurements fm
        ON (fm.id = ft.facial_measurement_id)
        LEFT JOIN masks m
        ON (m.id = ft.mask_id)
        WHERE ft.id = '#{id}'

        ORDER BY updated_at DESC
      SQL
    )

    self.json_parse(fit_tests, ["comfort", "results", "user_seal_check", "image_urls"])[0]
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


end
