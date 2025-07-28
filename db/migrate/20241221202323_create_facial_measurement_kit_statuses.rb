# frozen_string_literal: true

class CreateFacialMeasurementKitStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :facial_measurement_kit_statuses do |t|
      t.uuid :uuid, null: false
      t.datetime :refresh_datetime, null: false

      t.timestamps
    end

    add_index :facial_measurement_kit_statuses, %i[uuid refresh_datetime], unique: true,
                                                                           name: 'index_fmks_on_uuid_refr_datetime__unique_true'
  end
end
