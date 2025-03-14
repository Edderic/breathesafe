class ShippingStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    statuses = ShippingStatusBuilder.build
    statuses.each do |uuid, status|
      status['shippables'].each do |shippable|
        ShippingStatusJoin.create!(
          shipping_uuid: uuid,
          shippable_type: shippable['shippable_type'],
          shippable_uuid: shippable['shippable_uuid'],
          refresh_datetime: datetime
        )
      end

      status.delete('shippables')
      status['refresh_datetime'] = datetime
      status['uuid'] = uuid

      ShippingStatus.create!(**status)
    end
  end
end
