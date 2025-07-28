# frozen_string_literal: true

class CreateManagedUsers < ActiveRecord::Migration[7.0]
  def change
    create_table :managed_users do |t|
      t.references :manager, null: false, foreign_key: { to_table: :users }
      t.references :managed, null: false, foreign_key: { to_table: :users }

      t.timestamps
    end
  end
end
