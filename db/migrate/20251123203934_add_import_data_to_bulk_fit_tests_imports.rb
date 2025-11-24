# frozen_string_literal: true

class AddImportDataToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :import_data, :text
  end
end
