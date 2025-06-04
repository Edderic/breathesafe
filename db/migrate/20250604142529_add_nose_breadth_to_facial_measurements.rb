class AddNoseBreadthToFacialMeasurements < ActiveRecord::Migration[7.0]
  def change
    add_column :facial_measurements, :nose_breadth, :integer
  end
end
