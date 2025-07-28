# frozen_string_literal: true

class FacialMeasurementKitStatusBuilder
  def self.build
    actions = FacialMeasurementKitAction.all.order(:datetime)

    actions.each_with_object({}) do |action, accum|
      act_meta = action['metadata']
      case action.name
      when 'Create'
        accum[act_meta['uuid']] = {
          'digital_caliper_uuids' => [],
          'tape_measure_uuids' => []
        }

      when 'AddTapeMeasure'
        accum[act_meta['uuid']][
          'tape_measure_uuids'
        ] << act_meta['tape_measure_uuid']

      when 'AddDigitalCaliper'
        accum[act_meta['uuid']][
          'digital_caliper_uuids'
        ] << act_meta['digital_caliper_uuid']
      end
    end
  end
end
