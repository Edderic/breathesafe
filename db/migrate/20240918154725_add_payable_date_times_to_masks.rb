class AddPayableDateTimesToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :payable_datetimes, :json, default: []
  end
end
