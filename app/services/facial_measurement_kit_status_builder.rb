class FacialMeasurementKitStatusBuilder
  def self.build
    actions = FacialMeasurementKitAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      act_meta = action['metadata']
      if action.name == 'Create'
        accum[act_meta['uuid']] = {
          'digital_caliper_uuids' => [],
          'tape_measure_uuids' => []
        }

      elsif action.name == 'AddTapeMeasure'
        accum[act_meta['uuid']][
          'tape_measure_uuids'
        ] << act_meta['tape_measure_uuid']

      elsif action.name == 'AddDigitalCaliper'
        accum[act_meta['uuid']][
          'digital_caliper_uuids'
        ] << act_meta['digital_caliper_uuid']
      end

      accum
    end
  end
end
