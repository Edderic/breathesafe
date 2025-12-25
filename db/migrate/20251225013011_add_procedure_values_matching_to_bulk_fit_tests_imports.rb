# frozen_string_literal: true

class AddProcedureValuesMatchingToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :procedure_values_matching, :jsonb, default: {}, null: false
  end
end
