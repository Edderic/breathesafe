class AddMaximumOccupancyToEvents < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :maximum_occupancy, :integer
  end
end
