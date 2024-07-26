class AddFilterTypeToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :filter_type, :string
    remove_column :masks, :filter_types
  end
end
