# frozen_string_literal: true

class AddBrandIdToMasks < ActiveRecord::Migration[7.0]
  def change
    add_reference :masks, :brand, null: true, foreign_key: { on_delete: :nullify }
  end
end
