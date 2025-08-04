# frozen_string_literal: true

class AddUniqueIndexToMasks < ActiveRecord::Migration[7.0]
  def change
    add_index :masks, :unique_internal_model_code, unique: true, name: 'index_masks_on_unique_internal_model_code'
  end
end
