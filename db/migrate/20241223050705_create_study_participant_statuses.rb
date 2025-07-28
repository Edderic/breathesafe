# frozen_string_literal: true

class CreateStudyParticipantStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :study_participant_statuses do |t|
      t.uuid :study_uuid, null: false
      t.string :participant_uuid, null: false
      t.datetime :refresh_datetime
      t.datetime :interested_datetime
      t.datetime :accepted_datetime
      t.jsonb :removal_from_study, default: {}
      t.jsonb :qualifications, default: {}
      t.jsonb :equipment, default: {}

      t.timestamps
    end

    add_index :study_participant_statuses, %i[study_uuid participant_uuid refresh_datetime], unique: true,
                                                                                             name: 'index_stu_par_sta_on_study_uuid_participant_uuid_refr_dt'
  end
end
