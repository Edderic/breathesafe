# frozen_string_literal: true

class AddCurrentStateToMasks < ActiveRecord::Migration[7.0]
  def change
    add_column :masks, :current_state, :jsonb, default: {}, null: false, comment: 'Cached computed state from events'
    add_index :masks, :current_state, using: :gin
  end
end
