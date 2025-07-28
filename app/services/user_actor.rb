# frozen_string_literal: true

class UserActor
  def self.create(
    uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      name: 'CreateUser',
      datetime: datetime,
      metadata: {
        'uuid': uuid
      }
    )
  end

  def self.set_name(
    uuid:,
    first_name:,
    last_name:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      name: 'SetName',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'first_name' => first_name,
        'last_name' => last_name
      }
    )
  end

  def self.mark_high_risk(
    uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      name: 'MarkHighRisk',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'health_status': 'high_risk'
      }
    )
  end

  def self.set_address(
    uuid:,
    address_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      datetime: datetime,
      name: 'SetAddress',
      metadata: {
        'uuid' => uuid,
        'address_uuid' => address_uuid
      }
    )
  end

  def self.acknowledge_need_qlft_kit(
    uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      name: 'Actk',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'qlft_kit': {
          'need': true
        }
      }
    )
  end

  def self.acknowledged_have_received_mask_kit(
    uuid:,
    mask_kit_uuid:,
    datetime: nil
  )
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'UserAction',
      name: 'AcknowledgedHaveReceivedMaskKit',
      datetime: datetime,
      metadata: {
        'user_uuid': user_uuid,
        'mask_kit_uuid': mask_kit_uuid
      }
    )
  end
end
