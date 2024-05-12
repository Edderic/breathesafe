class AddExternalApiTokenToProfiles < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :external_api_token, :uuid
    add_column :profiles, :can_post_via_external_api, :boolean, default: true
  end
end
