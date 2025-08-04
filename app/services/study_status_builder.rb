# frozen_string_literal: true

class StudyStatusBuilder
  def self.build
    actions = StudyAction.all.order(:datetime)
    actions.each_with_object({}) do |action, accum|
      next unless action.name == 'Create'

      metadata = action.metadata

      accum[metadata['uuid']] = metadata
    end
  end
end
