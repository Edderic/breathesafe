class FacialMeasurementKitStatusBuilder
  def self.build
    actions = FacialMeasurementKitAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      if action.name == 'Create'
        accum[action['uuid']] = {
          'digital_caliper_uuids' => [],
          'tape_measure_uuids' => []
        }

      elsif action.name == 'AddTapeMeasure'
        accum[action['uuid']][
          'tape_measure_uuids'
        ] << action.metadata['tape_measure_uuid']

      elsif action.name == 'AddDigitalCaliper'
        accum[action['uuid']][
          'digital_caliper_uuids'
        ] << action.metadata['digital_caliper_uuid']
      end
    end
  end
end
