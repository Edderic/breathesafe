# frozen_string_literal: true

class NebulizerStatusBuilder
  def self.build
    nebulizer_actions = NebulizerAction.all.order(:datetime)

    nebulizer_actions.each_with_object({}) do |nebulizer_action, accum|
      uuid = nebulizer_action['metadata']['uuid']
      metadata = nebulizer_action['metadata']

      if nebulizer_action.name == 'CreateNebulizer'
        accum[uuid] = metadata
      elsif nebulizer_action.name == 'AddBatteries'
        accum[uuid]['power_supply']['batteries_present'] = true
        new_metadata = JSON.parse(metadata.to_json)
        new_metadata.delete('uuid')

        accum[uuid]['batteries'] << new_metadata
      elsif nebulizer_actions.name == 'RemoveBatteries'
        accum[uuid]['power_supply']['batteries_present'] = false
        accum[uuid]['batteries'] = []
      elsif nebulizer_action.name == 'Sanitize'
        accum[uuid]['sanitization'] << JSON.parse(metadata.to_json).delete('uuid')
      end
    end
  end
end
