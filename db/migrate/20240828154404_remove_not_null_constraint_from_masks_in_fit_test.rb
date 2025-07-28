# frozen_string_literal: true

class RemoveNotNullConstraintFromMasksInFitTest < ActiveRecord::Migration[7.0]
  def up
    change_column_null :fit_tests, :mask_id, true
  end

  def down
    change_column_null :fit_tests, :mask_id, false
  end
end
