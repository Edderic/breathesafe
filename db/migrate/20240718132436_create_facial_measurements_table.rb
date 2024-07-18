class CreateFacialMeasurementsTable < ActiveRecord::Migration[7.0]
  def change
    create_table :facial_measurements_tables do |t|
      t.references :user, null: false, foreign_key: true
      t.integer :face_width
      t.string :nose_bridge_height
      t.string :nose_bridge_breadth
      t.integer :jaw_width
      t.integer :face_depth
      t.integer :face_length
      t.string :lower_face_length
      t.integer :bitragion_menton_arc
      t.integer :bitragion_subnasale_arc
      t.string :cheek_fullness
      t.timestamps
    end
  end
end
