class ShippingActor
  def self.create_package(
    dimensions:,
    uuid: nil,
    datetime: nil,
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    if uuid.nil?
      uuid = SecureRandom.uuid
    end

    Action.create(
      type: 'ShippingAction',
      name: 'CreatePackage',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'dimensions': dimensions
      }
    )
  end

  def self.add_qualitative_fit_testing_kit(
    uuid:,
    qualitative_fit_testing_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'AddQualitativeFitTestingKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'qualitative_fit_testing_kit_uuid': qualitative_fit_testing_kit_uuid
      }
    )
  end

  def self.remove_qualitative_fit_testing_kit(
    uuid:,
    qualitative_fit_testing_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'RemoveQualitativeFitTestingKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'qualitative_fit_testing_kit_uuid': qualitative_fit_testing_kit_uuid
      }
    )
  end

  def self.add_mask_kit(
    uuid:,
    mask_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'AddMaskKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask_kit_uuid': mask_kit_uuid
      }
    )
  end

  def self.remove_mask_kit(
    uuid:,
    mask_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'RemoveMaskKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'mask_kit_uuid': mask_kit_uuid
      }
    )
  end

  def self.add_facial_measurement_kit(
    uuid:,
    facial_measurement_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'AddFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'facial_measurement_kit_uuid': facial_measurement_kit_uuid
      }
    )
  end

  def self.remove_facial_measurement_kit(
    uuid:,
    facial_measurement_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'RemoveFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'facial_measurement_kit_uuid': facial_measurement_kit_uuid
      }
    )
  end

  def self.set_from_address(
    uuid:,
    from_address_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'SetFromAddress',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'from_address_uuid': from_address_uuid
      }
    )
  end

  def self.set_to_address(
    uuid:,
    to_address_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'SetToAddress',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'to_address_uuid': to_address_uuid
      }
    )
  end

  def self.purchase_label(
    uuid:,
    purchase_label:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'PurchaseLabel',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'purchase_label': purchase_label
      }
    )
  end

  def self.send_to_courier(
    uuid:,
    send_to_courier_details:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'PurchaseLabel',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'send_to_courier_details': send_to_courier_details
      }
    )
  end

  def self.mark_delivered(
    uuid:,
    send_to_courier_details:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'MarkDelivered',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'status': 'delivered'
      }
    )
  end

  def self.mark_received(
    uuid:,
    receiver_user_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'MarkReceived',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'status': 'received',
        'receiver_user_uuid': receiver_user_uuid
      }
    )
  end
end

