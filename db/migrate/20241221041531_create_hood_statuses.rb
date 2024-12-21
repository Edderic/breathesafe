class CreateHoodStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :hood_statuses do |t|
      t.uuid :uuid, null: false
      t.datetime :refresh_datetime, null: false
      t.jsonb :how
      t.jsonb :cost
      t.string :model, null: false
      t.jsonb :weight
      t.jsonb :sanitization

      t.timestamps
    end

    add_index :hood_statuses, [:uuid, :refresh_datetime], unique: true
    add_index :hood_statuses, :uuid
  end
end
