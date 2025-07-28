# frozen_string_literal: true

class AddAuthorIdToMasks < ActiveRecord::Migration[7.0]
  def change
    add_reference :masks, :author, null: false, foreign_key: { to_table: :users }
    add_reference :fit_tests, :facial_measurement, null: false, foreign_key: true
  end
end
