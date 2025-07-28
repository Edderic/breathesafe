# frozen_string_literal: true

class CreateDigitalCaliperStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :digital_caliper_statuses do |t|
      t.uuid :uuid, null: false
      t.uuid :facial_measurement_kit_uuid
      t.datetime :refresh_datetime, null: false
      t.jsonb :how
      t.jsonb :cost
      t.string :model, null: false
      t.jsonb :weight
      t.jsonb :power_supply

      t.timestamps
    end

    add_index :digital_caliper_statuses, %i[uuid refresh_datetime facial_measurement_kit_uuid], unique: true,
                                                                                                name: 'index_dig_cal_sta_on_uuid_refr_fm_kit_uuid'
  end
end
