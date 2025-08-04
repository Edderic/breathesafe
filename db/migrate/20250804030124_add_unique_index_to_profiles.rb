# frozen_string_literal: true

class AddUniqueIndexToProfiles < ActiveRecord::Migration[7.0]
  def change
    remove_index :profiles, :user_id, if_exists: true
    add_index :profiles, :user_id, unique: true, name: 'index_profiles_on_user_id'
  end
end
