# frozen_string_literal: true

class CreateMaskPairs < ActiveRecord::Migration[7.0]
  def change
    create_table :mask_pairs do |t|
      t.references :mask_a, null: false, foreign_key: { to_table: :masks, on_delete: :restrict }
      t.references :mask_b, null: false, foreign_key: { to_table: :masks, on_delete: :restrict }
      t.jsonb :history, default: [], null: false
      t.float :name_distance, null: false

      t.timestamps
    end

    # Composite unique index to ensure only one pair exists for (mask_a_id, mask_b_id)
    # Note: Application logic should ensure mask_a_id < mask_b_id for consistency
    # Note: t.references already creates indexes on mask_a_id and mask_b_id for efficient lookups
    add_index :mask_pairs, %i[mask_a_id mask_b_id], unique: true

    # Check constraint to prevent self-reference (mask_a_id == mask_b_id)
    add_check_constraint :mask_pairs, 'mask_a_id != mask_b_id', name: 'check_mask_pair_not_self_reference'
  end
end
