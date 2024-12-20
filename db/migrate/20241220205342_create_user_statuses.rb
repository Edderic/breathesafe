class CreateUserStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :user_statuses do |t|
      t.uuid :uuid, null: false
      t.string :first_name
      t.string :last_name
      t.boolean :high_risk
      t.uuid :address_uuid
      t.datetime :refresh_datetime

      t.timestamps
    end
  end
end
