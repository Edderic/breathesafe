class StudyStatusBuilder
  def self.build(datetime: nil)
    actions = StudyAction.all.order(:datetime)
    actions.reduce({}) do |accum, action|
      if action.name == 'Create'
        metadata = action.metadata

        accum[metadata['uuid']] = metadata
      end

      accum
    end
  end
end
