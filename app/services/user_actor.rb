class UserActor
  def self.create(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'CreateUser',
      datetime: datetime,
      metadata: {
        'uuid': uuid
      }
    )
  end

  def self.set_name(
    uuid:,
    first_name:,
    last_name:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'SetName',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'first_name' => first_name,
        'last_name' => last_name
      }
    )
  end

  def self.mark_interested_in_study(
    uuid:,
    datetime: nil,
    study_name: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    if study_name.nil?
      study_name = 'Mask Recommender Based on Facial Features'
    end

    Action.create(
      type: 'UserAction',
      name: 'MarkInterestedInStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': study_name

      }
    )
  end

  def self.mark_high_risk(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'MarkHighRisk',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'health_status': 'high_risk'
      }
    )
  end

  def self.accept_into_study(
    uuid:,
    study_name: nil,
    datetime: nil
  )

    if datetime.nil?
      datetime = DateTime.now
    end

    if study_name.nil?
      study_name = 'Mask Recommender Based on Facial Features'
    end

    Action.create(
      type: 'UserAction',
      name: 'AcceptIntoStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': study_name
      }
    )
  end

  def self.remove_from_study(
    uuid:,
    reason:,
    study_name: nil,
    datetime: nil
  )

    if datetime.nil?
      datetime = DateTime.now
    end

    if study_name.nil?
      study_name = 'Mask Recommender Based on Facial Features'
    end

    Action.create(
      type: 'UserAction',
      name: 'RemoveFromStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': study_name,
        'reason': reason
      }
    )
  end

  def self.finish_study(
    uuid:,
    study: nil,
    datetime: nil
  )

    if datetime.nil?
      datetime = DateTime.now
    end

    if study.nil?
      study = 'Mask Recommender Based on Facial Features'
    end

    Action.create(
      type: 'UserAction',
      name: 'FinishStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': [
          study: study,
        ]
      }
    )
  end

  def self.set_address(
    uuid:,
    address_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      datetime: datetime,
      name: 'SetAddress',
      metadata: {
        'uuid' => uuid,
        'address_uuid' => address_uuid,
      }
    )
  end

  def self.acknowledge_need_qlft_kit(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'Actk',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'qlft_kit': {
          'need': true
        }
      }
    )
  end

  def self.mark_as_needing_facial_measurement_kit(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'MarkAsNeedingFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
      }
    )
  end

  def self.acknowledged_have_received_mask_kit(
    uuid:,
    mask_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'AcknowledgedHaveReceivedMaskKit',
      datetime: datetime,
      metadata: {
        'user_uuid': user_uuid,
        'mask_kit_uuid': mask_kit_uuid,
      }
    )
  end

  def self.acknowledged_have_received_facial_measurement_kit(
    user_uuid:,
    facial_measurement_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'AcknowledgedHaveReceivedFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'user_uuid': user_uuid,
        'facial_measurement_kit_uuid': facial_measurement_kit_uuid,
      }
    )
  end

  def self.acknowledged_have_received_qualitative_fit_testing_kit(
    user_uuid:,
    qualitative_fit_testing_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'AcknowledgedHaveReceivedQualitativeFitTestingKit',
      datetime: datetime,
      metadata: {
        'user_uuid': user_uuid,
        'qualitative_fit_testing_kit_uuid': qualitative_fit_testing_kit_uuid,
      }
    )
  end

  def self.set_goal_end_date(
    uuid:,
    end_date: nil,
    datetime: nil,
    study_name: nil
  )

    if study_name.nil?
      study_name = "Mask Recommender Based on Facial Features"
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    if end_date.nil?
      end_date = datetime + 4.months
    end

    Action.create(
      type: 'UserAction',
      name: 'SetGoalEndDate',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'study' => {
          'study_name' => study_name,
          'goal_end_date' => end_date
        }
      }
    )
  end

  def self.set_study_qualifications(
    uuid:,
    study_qualifications:,
    study_name: nil,
    datetime: nil
  )
    if study_name.nil?
      study_name = "Mask Recommender Based on Facial Features"
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'SetStudyQualifications',
      datetime: datetime,
      metadata: {
        'uuid'=> uuid,
        'study' => {
          'study_name' => study_name,
          'qualifications' => study_qualifications
        }
      }
    )
  end

  def self.request_for_equipment(
    uuid:,
    equipment_request:,
    study_name: nil,
    datetime: nil
  )
    if study_name.nil?
      study_name = "Mask Recommender Based on Facial Features"
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'RequestForEquipment',
      datetime: datetime,
      metadata: {
        'uuid'=> uuid,
        'study' => {
          'study_name' => study_name,
          'equipment_request' => equipment_request
        }
      }
    )
  end
end
