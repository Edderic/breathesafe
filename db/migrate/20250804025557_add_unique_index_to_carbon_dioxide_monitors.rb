# frozen_string_literal: true

class AddUniqueIndexToCarbonDioxideMonitors < ActiveRecord::Migration[7.0]
  def change
    add_index :carbon_dioxide_monitors, %i[serial model], unique: true,
                                                          name: 'index_carbon_dioxide_monitors_on_serial_and_model'
  end
end
