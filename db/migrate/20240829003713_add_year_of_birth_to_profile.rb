# frozen_string_literal: true

class AddYearOfBirthToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :year_of_birth, :integer
  end
end
