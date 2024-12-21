class CreateTapeMeasureStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :tape_measure_statuses do |t|
      t.uuid :uuid, null: false
      t.jsonb :cost
      t.string :model, null: false
      t.jsonb :weight
      t.datetime :refresh_datetime, null: false

      t.timestamps
    end

    add_index :tape_measure_statuses, [:uuid,:refresh_datetime], unique: true
  end
end
