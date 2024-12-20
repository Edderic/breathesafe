class FacialMeasurementKitActor
  def self.preset_create(uuid: nil, datetime: nil, digital_caliper_model: "8-inch iGaging" )
    if uuid.nil?
      uuid = SecureRandom.uuid
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    ActiveRecord::Base.transaction do
      kit_uuid = SecureRandom.uuid
      FacialMeasurementKitAction.create(
        datetime: datetime,
        name: 'Create',
        metadata: {
          'uuid' => kit_uuid
        }
      )

      digital_caliper_uuid = SecureRandom.uuid
      DigitalCaliperActor.create(
        model: digital_caliper_model,
        uuid: digital_caliper_uuid,
        datetime: datetime + 1.second
      )

      tape_measure_uuid = SecureRandom.uuid
      TapeMeasureActor.create(
        uuid: tape_measure_uuid,
        datetime: datetime + 1.second
      )

      self.add_tape_measure(
        uuid: kit_uuid,
        tape_measure_uuid: tape_measure_uuid,
        datetime: datetime + 2.second
      )

      self.add_digital_caliper(
        uuid: kit_uuid,
        digital_caliper_uuid: digital_caliper_uuid,
        datetime: datetime + 2.second
      )
    end
  end

  def self.add_tape_measure(uuid:, tape_measure_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    FacialMeasurementKitAction.create(
      name: 'AddTapeMeasure',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'tape_measure_uuid' => tape_measure_uuid
      }
    )
  end

  def self.add_digital_caliper(uuid:, digital_caliper_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    FacialMeasurementKitAction.create(
      name: 'AddDigitalCaliper',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'digital_caliper_uuid' => digital_caliper_uuid
      }
    )
  end
end
