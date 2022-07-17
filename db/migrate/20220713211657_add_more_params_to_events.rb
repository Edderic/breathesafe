class AddMoreParamsToEvents < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :ventilation_ach, :float
    add_column :events, :portable_ach, :float
    add_column :events, :room_usable_volume_cubic_meters, :float
    add_column :events, :total_ach, :float
  end
end
