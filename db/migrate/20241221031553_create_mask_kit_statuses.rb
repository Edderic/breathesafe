# frozen_string_literal: true

class CreateMaskKitStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :mask_kit_statuses do |t|
      t.uuid :uuid, null: false
      t.integer :mask_uuid, null: false
      t.datetime :refresh_datetime, null: false

      t.timestamps
    end

    add_index :mask_kit_statuses, %i[uuid mask_uuid refresh_datetime], unique: true,
                                                                       name: 'index_uuid_mask_uuid_datetime_on_mkst'
  end
end
