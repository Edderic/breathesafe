# frozen_string_literal: true

class DropMaskBreakdowns < ActiveRecord::Migration[7.0]
  def up
    drop_table :mask_breakdowns
  end

  def down
    # Recreate the table if needed to rollback
    create_table :mask_breakdowns do |t|
      t.references :mask, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true, comment: 'Admin user who created/edited this breakdown'
      t.jsonb :breakdown, null: true, default: []
      t.text :notes, comment: 'Optional notes about this breakdown'

      t.timestamps
    end

    add_index :mask_breakdowns, :breakdown, using: :gin
    add_index :mask_breakdowns, %i[mask_id updated_at], order: { updated_at: :desc }
  end
end
