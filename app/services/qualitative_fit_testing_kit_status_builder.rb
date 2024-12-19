class QualitativeFitTestingKitStatusBuilder
  def self.build
    qlft_kit_actions = QualitativeFitTestingKitAction.all.order(:datetime)
      # .where("type IN ('QualitativeFitTestingKitAction', 'HoodAction', 'NebulizerAction', 'SolutionAction')").all.order(:datetime)

    qlft_kit_actions.reduce({}) do |accum, qlft_kit_action|
      uuid = qlft_kit_action['metadata']['uuid']

      if qlft_kit_action.name == 'Create'
        accum[uuid] = {
          'solution_uuids' => [],
          'nebulizer_uuids' => [],
          'hood_uuids' => [],
        }
      elsif qlft_kit_action.name == 'AddSolution'
       accum[uuid]['solution_uuids'] << qlft_kit_action.metadata['solution_uuid']
      elsif qlft_kit_action.name == 'RemoveSolution'
        accum[uuid]['solution_uuids'].reject {|sol_uuid| sol_uuid == qlft_kit_action.metadata['solution_uuid']}
      elsif qlft_kit_action.name == 'AddNebulizer'
        accum[uuid]['nebulizer_uuids'] << qlft_kit_action.metadata['nebulizer_uuid']
      elsif qlft_kit_action.name == 'RemoveNebulizer'
        accum[uuid]['nebulizer_uuids'].reject {|neb_uuid| neb_uuid == qlft_kit_action.metadata['nebulizer_uuid']}
      elsif qlft_kit_action.name == 'AddHood'
        accum[uuid]['hood_uuids'] << qlft_kit_action.metadata['hood_uuid']
      elsif qlft_kit_action.name == 'RemoveHood'
        accum[uuid]['hood_uuids'].reject {|hood_uuid| qlft_kit_action.metadata['hood_uuid'] == hood_uuid}
      end

      accum
    end
  end
end
