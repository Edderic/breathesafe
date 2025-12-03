# frozen_string_literal: true

class AddComfortMatchingToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :comfort_matching, :jsonb, default: {}
  end
end
