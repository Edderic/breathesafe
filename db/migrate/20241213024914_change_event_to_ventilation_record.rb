# frozen_string_literal: true

class ChangeEventToVentilationRecord < ActiveRecord::Migration[7.0]
  def change
    rename_table :events, :ventilation_records
  end
end
