# frozen_string_literal: true

class CreateMeasurementDevices < ActiveRecord::Migration[7.0]
  def change
    create_table :measurement_devices do |t|
      t.string :manufacturer
      t.string :measurement_device_type
      t.string :model
      t.string :serial
      t.text :notes
      t.references :owner, null: false, foreign_key: { to_table: :users }

      t.timestamps
    end
  end
end
