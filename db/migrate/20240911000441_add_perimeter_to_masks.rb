# frozen_string_literal: true

class AddPerimeterToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :perimeter_mm, :float
  end
end
