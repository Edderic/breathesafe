class ChangeSexAssignedAtBirthToGenderAndSex < ActiveRecord::Migration[7.0]
  def change
    rename_column :profiles, :sex_assigned_at_birth, :gender_and_sex
  end
end
