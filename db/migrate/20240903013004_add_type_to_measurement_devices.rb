# frozen_string_literal: true

class AddTypeToMeasurementDevices < ActiveRecord::Migration[7.0]
  def change
    add_column :measurement_devices, :device_type, :string
  end
end
