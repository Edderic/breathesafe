class AddDemographicsToProfiles < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :demographics, :json
  end
end
