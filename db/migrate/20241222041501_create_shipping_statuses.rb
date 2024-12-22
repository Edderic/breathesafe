class CreateShippingStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :shipping_statuses do |t|
      t.uuid :uuid
      t.datetime :refresh_datetime, null: false
      t.uuid :to_user_uuid
      t.uuid :from_user_uuid
      t.jsonb :received
      t.jsonb :delivered
      t.uuid :from_address_uuid
      t.uuid :to_address_uuid
      t.jsonb :purchase_label
      t.jsonb :send_to_courier

      t.timestamps
    end

    add_index :shipping_statuses, [:uuid, :refresh_datetime], unique: true
  end
end
