require 'csv'

class State < ApplicationRecord
  def self.one_time_save
    path = File.join(
      File.dirname(
        File.dirname(
          File.dirname(
            File.absolute_path(__FILE__)
          )
        )
      ),
      'data/state_abbreviations.csv'
    )
    CSV.foreach(path, encoding: "bom|utf-8", headers: :first_row) do |r|
      self.create(full_name: r["State"], code: r["Code"])
    end
  end
end
