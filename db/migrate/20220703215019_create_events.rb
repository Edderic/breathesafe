class CreateEvents < ActiveRecord::Migration[7.0]
  def change
    create_table :events do |t|
      t.string :address
      t.string :room_name
      t.float :room_length_meters
      t.float :room_width_meters
      t.float :room_height_meters
      t.float :place_lat
      t.float :place_long
      t.datetime :start_datetime
      t.integer :duration_hours
      t.boolean :private
      t.text :portable_air_cleaners
      t.string :ventilation_co2_name
      t.string :ventilation_co2_serial
      t.string :ventilation_co2_model
      t.integer :ventilation_co2_steady_state_ppm
      t.integer :ventilation_co2_ambient_ppm
      t.text :ventilation_notes
      t.text :activity_groups
      t.integer :author_id

      t.timestamps
    end

    add_index :events, :address
    add_index :events, :author_id
  end
end
