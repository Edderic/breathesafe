# frozen_string_literal: true

class AddSourceFitTestIdToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_reference :fit_tests, :source_fit_test, foreign_key: { to_table: :fit_tests }, null: true
  end
end
