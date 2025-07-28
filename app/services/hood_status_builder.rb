# frozen_string_literal: true

class HoodStatusBuilder
  def self.build
    actions = HoodAction.all.order(:datetime)

    actions.each_with_object({}) do |action, accum|
      if action.name == 'CreateHood'
        accum[action.metadata['uuid']] = action.metadata
        accum[action.metadata['uuid']]['sanitization'] = []
      elsif action.name == 'Sanitize'
        accum[action.metadata['uuid']]['sanitization'] << {
          'sanitized_at' => action.datetime,
          'notes' => action.metadtaa['sanitize_notes']
        }
      end
    end
  end
end
