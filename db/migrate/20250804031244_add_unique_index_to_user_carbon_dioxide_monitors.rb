# frozen_string_literal: true

class AddUniqueIndexToUserCarbonDioxideMonitors < ActiveRecord::Migration[7.0]
  def change
    add_index :user_carbon_dioxide_monitors,
              %i[serial model user_id],
              unique: true,
              name: 'index_user_carbon_dioxide_monitors_on_serial_model_user_id'
  end
end
