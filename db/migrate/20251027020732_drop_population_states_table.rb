# frozen_string_literal: true

class DropPopulationStatesTable < ActiveRecord::Migration[7.0]
  # rubocop:disable Rails/ReversibleMigration
  def change
    drop_table :population_states, if_exists: true
  end
  # rubocop:enable Rails/ReversibleMigration
end
