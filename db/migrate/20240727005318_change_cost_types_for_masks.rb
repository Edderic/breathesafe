class ChangeCostTypesForMasks < ActiveRecord::Migration[7.0]
  def change
    rename_column :masks, :cost_us_dollars, :initial_cost_us_dollars
    add_column :masks, :filter_change_cost_us_dollars, :float
  end
end
