# frozen_string_literal: true

class AddMaskModdedValuesMatchingToBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    add_column :bulk_fit_tests_imports, :mask_modded_values_matching, :jsonb, default: {}, null: false
  end
end
