# frozen_string_literal: true

class StudyParticipantActor
  def self.set_snapshot(rows:, datetime:)
    datetime = DateTime.now if datetime.nil?

    rows.each do |row|
      row.delete('id')
      row.delete('refresh_datetime')
      row.delete('created_at')
      row.delete('updated_at')

      Action.create(
        type: 'StudyParticipantAction',
        name: 'SetSnapshot',
        datetime: datetime,
        metadata: row
      )
    end
  end

  def self.create(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'Create',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.mark_interested_in_study(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'MarkInterestedInStudy',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.set_study_qualifications(
    study_uuid:,
    participant_uuid:,
    study_qualifications:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'SetStudyQualifications',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid,
        'qualifications' => study_qualifications
      }
    )
  end

  def self.set_goal_end_date(
    study_uuid:,
    participant_uuid:,
    end_date: nil,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    end_date = datetime + 4.months if end_date.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'SetGoalEndDate',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid,
        'goal_end_date' => end_date
      }
    )
  end

  def self.accept_into_study(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'AcceptIntoStudy',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.remove_from_study(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'RemoveFromStudy',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.finish_study(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'FinishStudy',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.request_for_equipment(
    study_uuid:,
    participant_uuid:,
    equipment_request:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'RequestForEquipment',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid,
        'equipment_request' => equipment_request
      }
    )
  end

  def self.acknowledged_have_received_facial_measurement_kit(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'AcknowledgedHaveReceivedFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end

  def self.acknowledged_have_received_qualitative_fit_testing_kit(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'StudyParticipantAction',
      name: 'AcknowledgedHaveReceivedQualitativeFitTestingKit',
      datetime: datetime,
      metadata: {
        'study_uuid' => study_uuid,
        'participant_uuid' => participant_uuid
      }
    )
  end
end
