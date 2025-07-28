# frozen_string_literal: true

class SolutionStatusBuilder
  def self.build
    solution_actions = SolutionAction.all.order(:datetime)

    solution_actions.each_with_object({}) do |solution_action, accum|
      uuid = solution_action['metadata']['uuid']
      metadata = solution_action['metadata']

      if solution_action.name == 'CreateSolution'
        accum[uuid] = metadata
      elsif solution_action.name == 'EstimateVolume'
        accum[uuid]['volume_level_proportion'] = metadata['volume_level_proportion']
      else
        raise UnrecognizedActionError
      end
    end
  end
end
