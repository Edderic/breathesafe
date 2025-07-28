# frozen_string_literal: true

class FacialMeasurementKitActor
  def self.preset_create(uuid: nil, datetime: nil, digital_caliper_model: '8-inch iGaging')
    uuid = SecureRandom.uuid if uuid.nil?

    datetime = DateTime.now if datetime.nil?

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

      TapeMeasureActor.associate_with_facial_measurement_kit(
        uuid: tape_measure_uuid,
        facial_measurement_kit_uuid: uuid,
        datetime: datetime + 2.seconds
      )

      DigitalCaliperActor.associate_with_facial_measurement_kit(
        uuid: digital_caliper_uuid,
        facial_measurement_kit_uuid: uuid,
        datetime: datetime + 2.seconds
      )
    end
  end
end
