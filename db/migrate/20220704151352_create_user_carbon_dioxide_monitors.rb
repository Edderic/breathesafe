# frozen_string_literal: true

class CreateUserCarbonDioxideMonitors < ActiveRecord::Migration[7.0]
  def change
    create_table :user_carbon_dioxide_monitors do |t|
      t.references :user, null: false, foreign_key: true
      t.string :serial, null: false
      t.string :model, null: false

      t.timestamps
    end
  end
end
