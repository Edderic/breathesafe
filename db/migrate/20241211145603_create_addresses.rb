class CreateAddresses < ActiveRecord::Migration[7.0]
  def change
    create_table :addresses do |t|
      t.references :user, null: false, foreign_key: true
      t.string :start_datetime
      t.string :address_line_1
      t.string :address_line_2
      t.string :address_line_3
      t.string :town_city
      t.string :state
      t.string :country
      t.string :zipcode
      t.string :phone_number
      t.timestamps
    end
  end
end
