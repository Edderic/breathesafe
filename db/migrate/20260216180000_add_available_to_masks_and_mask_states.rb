# frozen_string_literal: true

class AddAvailableToMasksAndMaskStates < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :available, :boolean, null: false, default: true
    add_column :mask_states, :available, :boolean, null: false, default: true
    add_index :masks, :available
  end
end
