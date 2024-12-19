class SolutionStatusBuilder
  def self.build
    solution_actions = SolutionAction.all.order(:datetime)

    solution_actions.reduce({}) do |accum, solution_action|
      uuid = solution_action['metadata']['uuid']
      metadata = solution_action['metadata']

      if solution_action.name == 'CreateSolution'
        accum[uuid] = metadata
      elsif solution_action.name == 'EstimateVolume'
        accum[uuid]['volume_level_proportion'] = metadata['volume_level_proportion']
      else
        raise UnrecognizedActionError
      end

      accum
    end
  end
end
