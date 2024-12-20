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
      elsif shipping_action.name == 'PurchaseLabel'
        accum[metadata['uuid']]['purchase_label'] = metadata['purchase_label'].merge('datetime' => shipping_action.datetime)
      elsif shipping_action.name == 'SendToCourier'
        accum[metadata['uuid']]['send_to_courier'] = metadata['details'].merge('datetime' => shipping_action.datetime)
      elsif shipping_action.name == 'Deliver'
        accum[metadata['uuid']]['delivered'] = shipping_action.datetime
      elsif shipping_action.name == 'Receive'
        accum[metadata['uuid']]['received'] = shipping_action.datetime
      end

      accum
    end
  end
end
