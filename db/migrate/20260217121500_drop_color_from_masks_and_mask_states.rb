# frozen_string_literal: true

class DropColorFromMasksAndMaskStates < ActiveRecord::Migration[7.0]
  def change
    remove_column :masks, :color, :string
    remove_column :mask_states, :color, :string
  end
end
