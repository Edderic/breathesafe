class AddSocialsToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :socials, :jsonb
  end
end
