# frozen_string_literal: true

class AddMaskTypeToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :mask_type, :string
  end
end
