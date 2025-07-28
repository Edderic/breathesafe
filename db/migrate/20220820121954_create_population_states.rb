# frozen_string_literal: true

class CreatePopulationStates < ActiveRecord::Migration[7.0]
  def change
    create_table :population_states do |t|
      t.integer :population
      t.string :name

      t.timestamps
    end
  end
end
