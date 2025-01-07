class ShippingStatusBuilder
  def self.build
    shipping_actions = ShippingAction.all.order(:datetime)

    shipping_actions.reduce({}) do |accum, shipping_action|
      metadata = shipping_action['metadata']

      if shipping_action.name == 'CreatePackage'
        accum[metadata['uuid']] = {
          'shippables' => [],
          'purchase_label' => {},
          'send_to_courier' => {},
          'from_user_uuid' => nil,
          'to_user_uuid' => nil,
          'from_address_uuid' => nil,
          'to_address_uuid' => nil,
          'delivered' => {},
          'received' => {}
        }
      elsif shipping_action.name == 'AddItem'
        accum[metadata['uuid']]['shippables'] << {
          'shippable_uuid' => metadata['shippable_uuid'],
          'shippable_type' => metadata['shippable_type']
        }
      elsif shipping_action.name == 'RemoveItem'
        accum[metadata['uuid']]['shippables'].delete(metadata['shippable_uuid'])
      elsif shipping_action.name == 'SetFromAddress'
        accum[metadata['uuid']]['from_address_uuid'] = metadata['from_address_uuid']
      elsif shipping_action.name == 'SetToAddress'
        accum[metadata['uuid']]['to_address_uuid'] = metadata['to_address_uuid']
      elsif shipping_action.name == 'SetSender'
        accum[metadata['uuid']]['from_user_uuid'] = metadata['sender_uuid']
      elsif shipping_action.name == 'SetReceiver'
        accum[metadata['uuid']]['to_user_uuid'] = metadata['receiver_uuid']
      elsif shipping_action.name == 'PurchaseLabel'
        accum[metadata['uuid']]['purchase_label'] = metadata['purchase_label'].merge('datetime' => shipping_action.datetime)
        accum[metadata['uuid']]['purchase_label']['label_number'] = accum[metadata['uuid']]['purchase_label']['tracking_id']
        if accum[metadata['uuid']]['purchase_label'].key?('tracking_id')
          accum[metadata['uuid']]['purchase_label'].delete('tracking_id')
        end
      elsif shipping_action.name == 'SendToCourier'
        accum[metadata['uuid']]['send_to_courier'] = metadata['details'].merge('datetime' => shipping_action.datetime)
      elsif shipping_action.name == 'Deliver'
        accum[metadata['uuid']]['delivered'] = {
          'datetime' => shipping_action.datetime
        }
      elsif shipping_action.name == 'Receive'
        accum[metadata['uuid']]['received'] = {
          'datetime' => shipping_action.datetime
        }
      end

      accum
    end
  end
end
