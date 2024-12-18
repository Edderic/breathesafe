class UserActor
  def self.create(
    uuid: nil,
    datetime: nil
  )
    if uuid.nil?
      uuid = SecureRandom.uuid
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'CreateUser',
      datetime: datetime,
      metadata: {
        'uuid': SecureRandom.uuid
      }
    )
  end

  def self.mark_interested_in_study(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'MarkInterested',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': {
          study: 'Mask Recommender Based on Facial Features'
        }
      }
    )
  end

  def self.accept_into_study(
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
      name: 'AcceptIntoStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': {
          study: study,
        }
      }
    )
  end

  def self.remove_from_study(
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
      name: 'RemoveFromStudy',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'study': {
          study: study,
        }
      }
    )
  end

  def self.set_address(
    uuid:,
    address:
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
        'uuid': uuid,
        'address': address
      }
    )
  end


  def self.mark_as_needing_qlft_kit(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'UserAction',
      name: 'MarkAsNeedingQLFTKit',
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
end
