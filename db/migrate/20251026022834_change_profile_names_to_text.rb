# frozen_string_literal: true

class ChangeProfileNamesToText < ActiveRecord::Migration[7.0]
  # rubocop:disable Rails/BulkChangeTable
  def up
    # Change first_name and last_name columns to text type for encryption
    change_column :profiles, :first_name, :text
    change_column :profiles, :last_name, :text
  end

  def down
    # Revert back to string type
    change_column :profiles, :first_name, :string
    change_column :profiles, :last_name, :string
  end
  # rubocop:enable Rails/BulkChangeTable
end
