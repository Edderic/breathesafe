# frozen_string_literal: true

class DropCovidStates < ActiveRecord::Migration[7.0]
  def up
    drop_table :covid_states
  end

  def down
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
