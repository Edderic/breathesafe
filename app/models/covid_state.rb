# frozen_string_literal: true

class CovidState < ApplicationRecord
  def self.get_latest_date
    CovidState.connection.exec_query(
      <<-SQL
        select max(date) from covid_states
      SQL
    )[0]['max'].to_date
  end
end
