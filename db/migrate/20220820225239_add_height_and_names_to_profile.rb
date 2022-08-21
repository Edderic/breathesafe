class AddHeightAndNamesToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :first_name, :string
    add_column :profiles, :last_name, :string
    add_column :profiles, :height_meters, :float
  end
end
