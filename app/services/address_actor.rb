# frozen_string_literal: true

class AddressActor
  def self.stringify_address(address:)
    state_zip_code = "#{address[:state]} #{address[:zip_code]}"
    [
      address[:address_line_1],
      address[:address_line_2],
      address[:address_line_3],
      address[:town_city],
      state_zip_code,
      address[:country]
    ].select(&:present?).join(', ')
  end

  def self.find_or_create(address:, uuid: nil, factory: nil, datetime: nil)
    factory = RGeo::Geographic.simple_mercator_factory if factory.nil?

    datetime = DateTime.now if datetime.nil?

    uuid = SecureRandom.uuid if uuid.nil?

    stringified_address = stringify_address(address: address)
    created_address_actions = AddressAction.where(
      <<-SQL
      name = 'CreateAddress' AND
      metadata ->> 'stringified_address' = '#{stringified_address}'
      AND datetime < '#{datetime}'
      SQL
    ).order(:datetime)

    if created_address_actions.count.zero?
      search = Geocoder.search(stringified_address)
      search_item = search[0]

      point = if search_item
                factory.point(
                  search_item.data['lat'], search_item.data['lon']
                )
              else
                ''
              end

      AddressAction.create(
        name: 'CreateAddress',
        metadata: {
          uuid: uuid,
          stringified_address: stringified_address,
          address: address,
          address_coordinate: point.to_s
        }
      )

    else
      uuid = created_address_actions[0].metadata['uuid']
      # find the uuid for this address
    end

    uuid
  end
end
