# frozen_string_literal: true

class AddRemoveFromServiceToMeasurementDevices < ActiveRecord::Migration[7.0]
  def change
    add_column :measurement_devices, :remove_from_service, :boolean, default: false
  end
end
