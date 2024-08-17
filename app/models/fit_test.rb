class FitTest < ApplicationRecord
  belongs_to :mask
  belongs_to :facial_measurement

  def self.viewable(user)

    fit_tests = FitTest.connection.exec_query(
      <<-SQL
        SELECT ft.*, m.unique_internal_model_code, m.image_urls
        FROM fit_tests ft
        INNER JOIN facial_measurements fm
        ON (fm.id = ft.facial_measurement_id)
        INNER JOIN masks m
        ON (m.id = ft.mask_id)
        WHERE fm.user_id = #{user.id}
      SQL
    )

    self.json_parse(fit_tests, ["comfort", "results", "user_seal_check", "image_urls"])
  end

  def self.json_parse(events, columns)
    events.map do |ev|
      columns.each do |col|
        if !ev[col]
          ev[col] = []
        elsif col == "image_urls"
          ev[col] = JSON.parse(ev['image_urls'].gsub("{","[").gsub("}","]").gsub('\\',''))
        else
          ev[col] = JSON.parse(ev[col])
        end
      end

      ev
    end
  end


end
