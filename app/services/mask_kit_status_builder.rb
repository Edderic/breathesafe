class MaskKitStatusBuilder
  def self.build
    mask_kit_actions = MaskKitAction.all.order(:datetime)
    mask_kit_actions.reduce({}) do |accum, mask_kit_action|
      uuid =  mask_kit_action['metadata']['uuid']

      if mask_kit_action.name == 'CreateMaskKit'
        accum[uuid] = {
          'uuid' => uuid,
          'mask_uuids' => []
        }
      elsif mask_kit_action.name == 'AddMasks'
        accum[uuid]['mask_uuids'].union(mask_kit_action.metadata['mask_uuids'])
      elsif mask_kit_action.name == 'RemoveMasks'
        accum[uuid]['mask_uuids'] = \
          accum[uuid]['mask_uuids'] - mask_kit_action.metadata['mask_uuids']
      end

      accum
    end
  end
end
