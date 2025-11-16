# frozen_string_literal: true

class AddDuplicateOfToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :duplicate_of, :integer, null: true

    add_index :masks, :duplicate_of

    add_foreign_key :masks, :masks, column: :duplicate_of, on_delete: :nullify
  end
end
