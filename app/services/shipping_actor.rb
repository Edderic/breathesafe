require 'csv'

class ShippingActor
  def self.create_package(
    uuid: nil,
    datetime: nil
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
        'uuid': uuid
      }
    )
  end

  # Anything can be shippable. The type lets us know what tables should be
  # joined to e.g. Solution, QualitativeFitTestingKit, Hood
  # Mask, MaskKit,jj
  def self.add_item(
    uuid:,
    shippable_uuid:,
    shippable_type:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'AddItem',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'shippable_uuid': shippable_uuid,
        'shippable_type': shippable_type,
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

  def self.set_receiver(
    uuid:,
    receiver_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'SetReceiver',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'receiver_uuid': receiver_uuid
      }
    )
  end

  def self.set_sender(
    uuid:,
    sender_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'SetSender',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'sender_uuid': sender_uuid
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
    details:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'SendToCourier',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'details': details
      }
    )
  end

  def self.deliver(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'Deliver',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
      }
    )
  end

  def self.receive(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'ShippingAction',
      name: 'Receive',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
      }
    )
  end

  def self.bulk_assign_purchase_labels(csv_string)
    counter = 0
    header = []
    rows = []

    # Build a JSON-like representation of rows
    CSV.parse(csv_string) do |row|
      accum = {}

      if counter == 0
        header = row.map{|r| r.strip}
      else
        row.each.with_index do |value, index|
          accum[header[index]] = value.strip
        end
        rows << accum
      end
      counter += 1
    end

    shipping_statuses_add_labels_to = ShippingQuery.\
      find_shipping_statuses_with_blank_purchase_labels(user_status_names: rows.map{|r| r['name']})

    shipping_statuses_add_labels_to.each do |s|
      shipping_status_uuid = s['shipping_status_uuid']
      row = rows.find{ |r| r['name'] == s['first_name'] + ' ' + s['last_name']  }
      ShippingActor.purchase_label(uuid: shipping_status_uuid, purchase_label: row)
    end
  end
end

