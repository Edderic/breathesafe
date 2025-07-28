# frozen_string_literal: true

class AddColorsToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :colors, :jsonb, default: [], null: false
  end
end
