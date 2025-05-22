class MaskKitStatusBuilder
  def self.build(uuid: nil)
    if uuid.present?
      mask_kit_actions = MaskKitAction.where("metadata ->> 'uuid' = '#{uuid}'").order(:datetime)
    else
      mask_kit_actions = MaskKitAction.all.order(:datetime)
    end

    mask_kit_actions.reduce({}) do |accum, mask_kit_action|
      uuid =  mask_kit_action['metadata']['uuid']

      if mask_kit_action.name == 'CreateMaskKit'
        accum[uuid] = {
          'uuid' => uuid,
          'mask_uuids' => []
        }
      elsif mask_kit_action.name == 'AddMasks'
        # Assumption right now is mask_uuids is an item
        accum[uuid]['mask_uuids'] << mask_kit_action.metadata['mask_uuids']
      elsif mask_kit_action.name == 'RemoveMasks'
        accum[uuid]['mask_uuids'] = \
          accum[uuid]['mask_uuids'] - mask_kit_action.metadata['mask_uuids']
      elsif mask_kit_action.name == 'UpdateMaskId'
        accum[uuid]['mask_uuids'] -= [mask_kit_action.metadata['from_mask_uuid']]
        accum[uuid]['mask_uuids'] += [mask_kit_action.metadata['to_mask_uuid']]
      end

      accum
    end
  end
end
