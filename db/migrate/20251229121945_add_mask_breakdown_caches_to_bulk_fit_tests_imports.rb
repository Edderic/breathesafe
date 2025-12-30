# frozen_string_literal: true

class AddMaskBreakdownCachesToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports,
               :from_file_mask_breakdowns,
               :jsonb,
               default: {},
               null: false

    add_column :bulk_fit_tests_imports,
               :from_file_mask_breakdown_errors,
               :jsonb,
               default: {},
               null: false
  end
end
