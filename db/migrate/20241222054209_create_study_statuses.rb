class CreateStudyStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :study_statuses do |t|
      t.uuid :uuid, null: false
      t.string :name, null: false
      t.datetime :refresh_datetime, null: false

      t.timestamps
    end

    add_index :study_statuses, [:uuid, :name, :refresh_datetime], unique: true
  end
end
