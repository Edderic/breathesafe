# frozen_string_literal: true

class AddBulkFitTestsImportIdToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_reference :fit_tests, :bulk_fit_tests_import, null: true, foreign_key: true
  end
end
