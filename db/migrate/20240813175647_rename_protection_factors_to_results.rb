class RenameProtectionFactorsToResults < ActiveRecord::Migration[7.0]
  def change
    rename_column :fit_tests, :protection_factors, :results
  end
end
