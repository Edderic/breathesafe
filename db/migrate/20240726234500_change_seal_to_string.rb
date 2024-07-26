class ChangeSealToString < ActiveRecord::Migration[7.0]
  def change
    remove_column :masks, :seal, :boolean
    add_column :masks, :seal, :string
  end
end
