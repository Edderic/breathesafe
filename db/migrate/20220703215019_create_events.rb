class CreateEvents < ActiveRecord::Migration[7.0]
  def change
    create_table :events do |t|
      t.jsonb :portable_air_cleaners
      t.float :room_width_meters
      t.float :room_length_meters
      t.float :room_height_meters
      t.string :room_name
      t.float :room_usable_volume_factor
      t.jsonb :place_data
      t.jsonb :activity_groups
      t.float :ventilation_co2_ambient_ppm
      t.string :ventilation_co2_measurement_device_name
      t.string :ventilation_co2_measurement_device_model
      t.string :ventilation_co2_measurement_device_serial
      t.float :ventilation_co2_steady_state_ppm
      t.text :ventilation_notes
      t.datetime :start_datetime
      t.string :duration
      t.boolean :private
      t.integer :author_id, null: false
      t.jsonb :occupancy

      t.timestamps
    end

    add_index :events, :author_id
  end
end
