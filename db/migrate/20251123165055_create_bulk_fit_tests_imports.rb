# frozen_string_literal: true

class CreateBulkFitTestsImports < ActiveRecord::Migration[7.0]
  def change
    create_table :bulk_fit_tests_imports do |t|
      t.references :user, null: false, foreign_key: true
      t.string :source_name, null: false
      t.string :source_type, null: false
      t.jsonb :column_matching_mapping, default: {}
      t.text :user_matching, default: '{}'
      t.jsonb :mask_matching, default: {}
      t.json :user_seal_check_matching, default: {}
      t.json :fit_testing_matching, default: {}
      t.string :status, default: 'pending'

      t.timestamps
    end
  end
end
