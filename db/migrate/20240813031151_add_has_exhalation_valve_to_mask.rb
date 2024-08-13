class AddHasExhalationValveToMask < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :has_exhalation_valve, :boolean
  end
end
