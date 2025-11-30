# frozen_string_literal: true

class AddTestingModeMatchingToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :testing_mode_matching, :jsonb, default: {}
  end
end
