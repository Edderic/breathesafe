class CreateAddressStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :address_statuses do |t|
      t.uuid :uuid, null: false
      t.string :address_line_1, null: false
      t.string :address_line_2
      t.string :address_line_3
      t.string :town_city, null: false
      t.string :country, null: false
      t.string :state, null: false
      t.string :zip_code, null: false
      t.geometry :address_coordinate
      t.string :stringified_address, null: false
      t.timestamps
    end
  end
end
