# frozen_string_literal: true

class MaskKitStatusBuilder
  def self.build(uuid: nil)
    mask_kit_actions = if uuid.present?
                         MaskKitAction.where("metadata ->> 'uuid' = '#{uuid}'").order(:datetime)
                       else
                         MaskKitAction.all.order(:datetime)
                       end

    mask_kit_actions.each_with_object({}) do |mask_kit_action, accum|
      uuid = mask_kit_action['metadata']['uuid']

      case mask_kit_action.name
      when 'CreateMaskKit'
        accum[uuid] = {
          'uuid' => uuid,
          'mask_uuids' => []
        }
      when 'AddMasks'
        # Assumption right now is mask_uuids is an item
        accum[uuid]['mask_uuids'] << mask_kit_action.metadata['mask_uuids']
      when 'RemoveMasks'
        accum[uuid]['mask_uuids'] = \
          accum[uuid]['mask_uuids'] - mask_kit_action.metadata['mask_uuids']
      when 'UpdateMaskId'
        accum[uuid]['mask_uuids'] -= [mask_kit_action.metadata['from_mask_uuid']]
        accum[uuid]['mask_uuids'] += [mask_kit_action.metadata['to_mask_uuid']]
      end
    end
  end
end
