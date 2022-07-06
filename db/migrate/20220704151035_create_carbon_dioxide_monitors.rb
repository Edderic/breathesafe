class CreateCarbonDioxideMonitors < ActiveRecord::Migration[7.0]
  def change
    create_table :carbon_dioxide_monitors do |t|
      t.string :name
      t.string :model
      t.string :serial

      t.timestamps
    end
    add_index :carbon_dioxide_monitors, :serial
  end
end
