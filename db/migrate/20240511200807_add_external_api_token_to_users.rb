class AddExternalApiTokenToUsers < ActiveRecord::Migration[7.0]
  def change
    add_column :users, :external_api_token, :uuid
    add_column :users, :can_post_via_external_api, :boolean, default: true
  end
end
