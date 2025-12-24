# frozen_string_literal: true

class AddModificationsToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_column :fit_tests, :modifications, :boolean, default: false, null: false
  end
end
