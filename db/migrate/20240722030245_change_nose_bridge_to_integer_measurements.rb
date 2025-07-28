# frozen_string_literal: true

class ChangeNoseBridgeToIntegerMeasurements < ActiveRecord::Migration[7.0]
  def change
    remove_column :facial_measurements, :nose_bridge_breadth
    remove_column :facial_measurements, :nose_bridge_height
    add_column :facial_measurements, :nasal_root_breadth, :integer
    add_column :facial_measurements, :nose_protrusion, :integer
    add_column :facial_measurements, :nose_bridge_height, :integer
    add_column :facial_measurements, :lip_width, :integer
  end
end
