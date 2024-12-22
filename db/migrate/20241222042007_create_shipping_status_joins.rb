class CreateShippingStatusJoins < ActiveRecord::Migration[7.0]
  def change
    create_table :shipping_status_joins do |t|
      t.datetime :refresh_datetime, null: false
      t.string :shippable_type, null: false
      t.uuid :shipping_uuid, null: false
      t.uuid :shippable_uuid, null: false

      t.timestamps
    end

    add_index :shipping_status_joins, [:shipping_uuid, :shippable_uuid, :refresh_datetime],
      name: 'index_ssj_on_ship_uuid_shippable_uuid_refresh_datetime'
  end
end
