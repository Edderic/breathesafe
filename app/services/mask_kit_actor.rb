# frozen_string_literal: true

class MaskKitActor
  def self.create(uuid: nil, datetime: nil)
    datetime = DateTime.now if datetime.nil?

    uuid = SecureRandom.uuid if uuid.nil?

    Action.create(
      type: 'MaskKitAction',
      name: 'CreateMaskKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid
      }
    )
  end

  def self.add_masks(uuid:, mask_uuids:, datetime:)
    Action.create(
      type: 'MaskKitAction',
      name: 'AddMasks',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask_uuids': mask_uuids
      }
    )
  end

  def self.remove_masks(uuid:, mask_uuids:, datetime:, by_uuid:)
    Action.create(
      type: 'MaskKitAction',
      name: 'RemoveMasks',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask_uuids': mask_uuids,
        'by_uuid': by_uuid
      }
    )
  end

  def self.update_mask_id(uuid:, from_mask_uuid:, to_mask_uuid:, datetime: nil)
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'MaskKitAction',
      name: 'UpdateMaskId',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'from_mask_uuid': from_mask_uuid,
        'to_mask_uuid': to_mask_uuid
      }
    )
  end

  def self.add_default_masks(uuid:, datetime:)
    masks = Mask.where('json_array_length(payable_datetimes) > 0')

    masks.each do |m|
      add_masks(
        uuid: uuid,
        mask_uuids: m.id,
        datetime: datetime
      )
    end
  end
end
