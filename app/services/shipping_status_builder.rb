# frozen_string_literal: true

class ShippingStatusBuilder
  def self.build
    shipping_actions = ShippingAction.all.order(:datetime)

    shipping_actions.each_with_object({}) do |shipping_action, accum|
      metadata = shipping_action['metadata']

      case shipping_action.name
      when 'CreatePackage'
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
      when 'AddItem'
        accum[metadata['uuid']]['shippables'] << {
          'shippable_uuid' => metadata['shippable_uuid'],
          'shippable_type' => metadata['shippable_type']
        }
      when 'RemoveItem'
        accum[metadata['uuid']]['shippables'].delete(metadata['shippable_uuid'])
      when 'SetFromAddress'
        accum[metadata['uuid']]['from_address_uuid'] = metadata['from_address_uuid']
      when 'SetToAddress'
        accum[metadata['uuid']]['to_address_uuid'] = metadata['to_address_uuid']
      when 'SetSender'
        accum[metadata['uuid']]['from_user_uuid'] = metadata['sender_uuid']
      when 'SetReceiver'
        accum[metadata['uuid']]['to_user_uuid'] = metadata['receiver_uuid']
      when 'PurchaseLabel'
        accum[metadata['uuid']]['purchase_label'] =
          metadata['purchase_label'].merge('datetime' => shipping_action.datetime)
        accum[metadata['uuid']]['purchase_label']['label_number'] =
          accum[metadata['uuid']]['purchase_label']['tracking_id']
        if accum[metadata['uuid']]['purchase_label'].key?('tracking_id')
          accum[metadata['uuid']]['purchase_label'].delete('tracking_id')
        end
      when 'SendToCourier'
        accum[metadata['uuid']]['send_to_courier'] = metadata['details'].merge('datetime' => shipping_action.datetime)
      when 'Deliver'
        accum[metadata['uuid']]['delivered'] = {
          'datetime' => shipping_action.datetime
        }
      when 'Receive'
        accum[metadata['uuid']]['received'] = {
          'datetime' => shipping_action.datetime
        }
      end
    end
  end
end
