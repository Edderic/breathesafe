# frozen_string_literal: true

class AddBulkFitTestsImportIdToMasks < ActiveRecord::Migration[7.0]
  def change
    add_reference :masks, :bulk_fit_tests_import, null: true, foreign_key: true
  end
end
