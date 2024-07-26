class ChangeSomeColumnsInMasks < ActiveRecord::Migration[7.0]
  def change
    rename_column :masks, :elastomeric, :seal
    add_column :masks, :filtration_efficiencies, :jsonb
    add_column :masks, :strap_type, :string
    add_column :masks, :mass_grams, :string
    add_column :masks, :height_mm, :string
    add_column :masks, :width_mm, :string
    add_column :masks, :depth_mm, :string
    add_column :masks, :has_gasket, :boolean
    add_column :masks, :pressure_drops, :jsonb
    add_column :masks, :cost_us_dollars, :float
    add_column :masks, :source, :string
    add_column :masks, :notes, :text
  end
end
