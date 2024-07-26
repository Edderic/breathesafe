class AddDefaultEmptyHashToMasks < ActiveRecord::Migration[7.0]
  def change
    remove_column :masks, :filtration_efficiencies, :jsonb
    add_column :masks, :filtration_efficiencies, :jsonb, default: []
    remove_column :masks, :pressure_drops, :jsonb
    add_column :masks, :pressure_drops, :jsonb, default: []
  end
end
