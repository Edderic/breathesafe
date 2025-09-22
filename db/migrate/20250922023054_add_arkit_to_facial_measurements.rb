class AddArkitToFacialMeasurements < ActiveRecord::Migration[7.0]
  def change
    add_column :facial_measurements, :arkit, :jsonb
  end
end
