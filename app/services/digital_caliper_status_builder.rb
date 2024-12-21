class DigitalCaliperStatusBuilder
  def self.build
    actions = DigitalCaliperAction.all.order(:datetime)
    actions.reduce({}) do |accum, action|
      if action.name == 'CreateDigitalCaliper'
        accum[action.metadata['uuid']] = action.metadata
      end

      accum
    end
  end
end
