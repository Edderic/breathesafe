class MaskKitActor
  def self.create(uuid: nil, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    if uuid.nil?
      uuid = SecureRandom.uuid
    end

    Action.create(
      type: 'MaskKitAction',
      name: 'CreateMaskKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid
      }
    )
  end

  def self.add_masks(uuid:, mask_uuids:)
    Action.create(
      type: 'MaskKitAction',
      name: 'AddMasks',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask_uuids': masks
      }
    )
  end

  def self.remove_masks(uuid:, mask_uuids:)
    Action.create(
      type: 'MaskKitAction',
      name: 'RemoveMasks',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask': mask_uuids
      }
    )
  end

  def self.add_default_masks(uuid:)
    masks = Mask.where('json_array_length(payable_datetimes) > 0')

    masks.each do |m|
      self.add_masks(uuid: uuid, mask_uuids: masks.id)
    end
  end
end
