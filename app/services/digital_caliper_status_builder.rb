# frozen_string_literal: true

class DigitalCaliperStatusBuilder
  def self.build
    actions = DigitalCaliperAction.all.order(:datetime)
    actions.each_with_object({}) do |action, accum|
      case action.name
      when 'CreateDigitalCaliper'
        accum[action.metadata['uuid']] = action.metadata
      when 'AssociateFacialMeasurementKit'
        accum[action.metadata['uuid']]['facial_measurement_kit_uuid'] = \
          action.metadata['facial_measurement_kit_uuid']
      when 'DissociateFacialMeasurementKit'
        accum[action.metadata['uuid']]['facial_measurement_kit_uuid'] = nil
      end
    end
  end
end
