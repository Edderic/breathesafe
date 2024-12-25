class StudyParticipantStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    statuses = StudyParticipantStatusBuilder.build

    statuses.each do |study_uuid, participants|
      participants.each do |participant_uuid, participant|
        participant['participant_uuid'] = participant_uuid
        participant['study_uuid'] = study_uuid
        participant['refresh_datetime'] = datetime

        StudyParticipantStatus.create!(
          **participant
        )
      end
    end
  end
end
