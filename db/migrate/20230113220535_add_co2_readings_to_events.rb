# frozen_string_literal: true

class AddCo2ReadingsToEvents < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :co2_readings, :jsonb
  end
end
