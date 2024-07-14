class AddRaceEthnicityGenderToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :race_ethnicity, :string
    add_column :profiles, :sex_assigned_at_birth, :string
  end
end
