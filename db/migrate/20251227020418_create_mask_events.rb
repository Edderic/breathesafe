# frozen_string_literal: true

class CreateMaskEvents < ActiveRecord::Migration[7.0]
  def change
    create_table :mask_events do |t|
      t.references :mask, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true, comment: 'Admin user who created this event'
      t.string :event_type, null: false, comment: 'Type of event (e.g., breakdown_updated, color_changed)'
      t.jsonb :data, null: false, default: {}, comment: 'Event-specific payload'
      t.text :notes, comment: 'Optional notes about this event'

      t.timestamps
    end

    # Indexes for efficient querying
    add_index :mask_events, %i[mask_id created_at], order: { created_at: :asc }
    add_index :mask_events, :event_type
    add_index :mask_events, :data, using: :gin
  end
end
