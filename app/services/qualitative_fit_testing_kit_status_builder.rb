# frozen_string_literal: true

class QualitativeFitTestingKitStatusBuilder
  def self.build
    qlft_kit_actions = QualitativeFitTestingKitAction.all.order(:datetime)

    qlft_kit_actions.each_with_object({}) do |qlft_kit_action, accum|
      uuid = qlft_kit_action['metadata']['uuid']

      case qlft_kit_action.name
      when 'Create'
        accum[uuid] = {
          'solution_uuids' => [],
          'nebulizer_uuids' => [],
          'hood_uuids' => []
        }
      when 'AddSolution'
        accum[uuid]['solution_uuids'] << qlft_kit_action.metadata['solution_uuid']
      when 'RemoveSolution'
        accum[uuid]['solution_uuids'].reject { |sol_uuid| sol_uuid == qlft_kit_action.metadata['solution_uuid'] }
      when 'AddNebulizer'
        accum[uuid]['nebulizer_uuids'] << qlft_kit_action.metadata['nebulizer_uuid']
      when 'RemoveNebulizer'
        accum[uuid]['nebulizer_uuids'].reject { |neb_uuid| neb_uuid == qlft_kit_action.metadata['nebulizer_uuid'] }
      when 'AddHood'
        accum[uuid]['hood_uuids'] << qlft_kit_action.metadata['hood_uuid']
      when 'RemoveHood'
        accum[uuid]['hood_uuids'].reject { |hood_uuid| qlft_kit_action.metadata['hood_uuid'] == hood_uuid }
      end
    end
  end
end
