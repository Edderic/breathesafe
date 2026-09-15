# frozen_string_literal: true

class CreateAnonymousContributions < ActiveRecord::Migration[7.0]
  def change
    create_table :anonymous_participants do |t|
      t.string :credential_digest, null: false
      t.timestamps
    end
    add_index :anonymous_participants, :credential_digest, unique: true

    create_table :anonymous_contributions do |t|
      t.references :anonymous_participant, null: false, foreign_key: true
      t.uuid :contribution_id, null: false
      t.integer :measurement_version, null: false
      t.jsonb :measurements, null: false
      t.jsonb :fit_tests, null: false, default: []
      t.string :consent_version, null: false
      t.datetime :consent_accepted_at, null: false
      t.string :payload_digest, null: false
      t.timestamps
    end
    add_index :anonymous_contributions, :contribution_id, unique: true
  end
end
