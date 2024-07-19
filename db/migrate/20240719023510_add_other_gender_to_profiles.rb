class AddOtherGenderToProfiles < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :other_gender, :string
  end
end
