# frozen_string_literal: true

class CreateMaskProposals < ActiveRecord::Migration[7.0]
  def change
    create_table :mask_proposals do |t|
      t.string :name, null: false
      t.string :normalized_name, null: false
      t.references :mask, foreign_key: true
      t.references :reviewer, foreign_key: { to_table: :users }
      t.datetime :resolved_at
      t.datetime :notified_at
      t.timestamps
    end
    add_index :mask_proposals, :normalized_name, unique: true
    create_table :mask_proposal_links do |t|
      t.references :mask_proposal, null: false, foreign_key: true
      t.references :anonymous_contribution, null: false, foreign_key: true, index: false
      t.integer :test_index, null: false
      t.timestamps
    end
    add_index :mask_proposal_links,
              %i[anonymous_contribution_id test_index],
              unique: true,
              name: 'index_mask_proposal_links_on_contribution_and_test'
  end
end
