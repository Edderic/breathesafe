# frozen_string_literal: true

class PopulationState < ApplicationRecord
  def self.upload
    delete_all

    path = File.join(
      File.dirname(
        File.dirname(
          File.dirname(
            File.absolute_path(__FILE__)
          )
        )
      ),
      'data/NST-EST2021-alldata.csv'
    )
    CSV.foreach(path, encoding: 'bom|utf-8', headers: :first_row) do |r|
      create(name: r['NAME'], population: r['POPESTIMATE2021'])
    end
  end
end
