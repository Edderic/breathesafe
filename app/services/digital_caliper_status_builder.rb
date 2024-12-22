class DigitalCaliperStatusBuilder
  def self.build
    actions = DigitalCaliperAction.all.order(:datetime)
    actions.reduce({}) do |accum, action|
      if action.name == 'CreateDigitalCaliper'
        accum[action.metadata['uuid']] = action.metadata
      elsif action.name == 'AssociateFacialMeasurementKit'
        accum[action.metadata['uuid']]['facial_measurement_kit_uuid'] = \
          action.metadata['facial_measurement_kit_uuid']
      elsif action.name == 'DissociateFacialMeasurementKit'
        accum[action.metadata['uuid']]['facial_measurement_kit_uuid'] = nil
      end

      accum
    end
  end
end
