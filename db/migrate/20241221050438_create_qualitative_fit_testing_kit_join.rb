class CreateQualitativeFitTestingKitJoin < ActiveRecord::Migration[7.0]
  def change
    create_table :qualitative_fit_testing_kit_joins do |t|
      t.uuid :qlft_kit_uuid, null: false
      t.uuid :part_uuid, null: false
      t.string :part_type, null: false
      t.datetime :refresh_datetime, null: false

      t.timestamps
    end

    add_index :qualitative_fit_testing_kit_joins,
      [
        :qlft_kit_uuid,
        :part_uuid,
        :refresh_datetime
      ],
      unique: true,
      name: 'index_qlft_kit_join_on_qlft_kit_uuid_part_uuid_refresh_datetime'
  end
end
