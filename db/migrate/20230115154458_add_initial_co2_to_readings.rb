# frozen_string_literal: true

class AddInitialCo2ToReadings < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :initial_co2, :integer
  end
end
