# frozen_string_literal: true

class AddApprovedByToEvents < ActiveRecord::Migration[7.0]
  def change
    add_column :events, :approved_by_id, :integer
  end
end
