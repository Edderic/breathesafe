class ChangeColumnCo2ReadingsToEvents < ActiveRecord::Migration[7.0]
  def change
    rename_column :events, :co2_readings, :sensor_data
  end
end
