class StudyParticipantActor
  def self.create(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'StudyParticipantAction',
      name: 'SetStudyQualifications',
      datetime: datetime,
      metadata: {
        'study_uuid'=> study_uuid,
        'participant_uuid'=> participant_uuid,
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

    if datetime.nil?
      datetime = DateTime.now
    end

    if end_date.nil?
      end_date = datetime + 4.months
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'StudyParticipantAction',
      name: 'RequestForEquipment',
      datetime: datetime,
      metadata: {
        'study_uuid'=> study_uuid,
        'participant_uuid'=> participant_uuid,
        'equipment_request' => equipment_request
      }
    )
  end

  def self.acknowledged_have_received_facial_measurement_kit(
    study_uuid:,
    participant_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

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
    if datetime.nil?
      datetime = DateTime.now
    end

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
