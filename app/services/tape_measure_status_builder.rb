class TapeMeasureStatusBuilder
  def self.build
    actions = TapeMeasureAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      if action.name == 'CreateTapeMeasure'
        accum[action.metadata['uuid']] = action.metadata
      end

      accum
    end
  end
end
