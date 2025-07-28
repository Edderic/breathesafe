# frozen_string_literal: true

class CreateCovidStates < ActiveRecord::Migration[7.0]
  def change
    create_table :covid_states do |t|
      t.date :date
      t.string :state
      t.integer :fips
      t.integer :cases_cumulative
      t.integer :deaths_cumulative

      t.timestamps
    end
  end
end
