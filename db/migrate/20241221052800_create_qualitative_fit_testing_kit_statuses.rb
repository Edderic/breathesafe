# frozen_string_literal: true

class CreateQualitativeFitTestingKitStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :qualitative_fit_testing_kit_statuses do |t|
      t.uuid :uuid
      t.datetime :refresh_datetime
      t.string :type

      t.timestamps
    end

    add_index :qualitative_fit_testing_kit_statuses, %i[uuid refresh_datetime type], unique: true,
                                                                                     name: 'index_qlft_kit_on_uuid_refresh_datetime_type_unique_true'
  end
end
