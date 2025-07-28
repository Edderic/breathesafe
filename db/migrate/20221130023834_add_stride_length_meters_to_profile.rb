# frozen_string_literal: true

class AddStrideLengthMetersToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :stride_length_meters, :float
  end
end
