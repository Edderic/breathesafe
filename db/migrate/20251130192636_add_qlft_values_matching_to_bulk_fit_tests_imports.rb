# frozen_string_literal: true

class AddQlftValuesMatchingToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :qlft_values_matching, :jsonb, default: {}
  end
end
