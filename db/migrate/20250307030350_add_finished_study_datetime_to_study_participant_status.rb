# frozen_string_literal: true

class AddFinishedStudyDatetimeToStudyParticipantStatus < ActiveRecord::Migration[7.0]
  def change
    add_column :study_participant_statuses, :finished_study_datetime, :datetime
  end
end
