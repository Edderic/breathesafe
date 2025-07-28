# frozen_string_literal: true

class TapeMeasureStatusBuilder
  def self.build
    actions = TapeMeasureAction.all.order(:datetime)

    actions.each_with_object({}) do |action, accum|
      accum[action.metadata['uuid']] = action.metadata if action.name == 'CreateTapeMeasure'
    end
  end
end
