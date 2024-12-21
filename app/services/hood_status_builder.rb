class HoodStatusBuilder
  def self.build
    actions = HoodAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      if action.name == 'CreateHood'
        accum[action.metadata['uuid']] = action.metadata
        accum[action.metadata['uuid']]['sanitization'] = []
      elsif action.name == 'Sanitize'
        accum[action.metadata['uuid']]['sanitization'] << {
          'sanitized_at' => action.datetime,
          'notes' => action.metadtaa['sanitize_notes']
        }
      end

      accum
    end
  end
end
