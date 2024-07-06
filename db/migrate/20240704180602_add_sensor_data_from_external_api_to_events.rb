class AddSensorDataFromExternalApiToEvents < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :sensor_data_from_external_api, :boolean, default: false
  end
end
