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
    ].select{|x| x.present?}.join(', ')
  end

  def self.save_address(uuid:, address:, factory: nil)
      if factory.nil?
        factory = RGeo::Geographic.simple_mercator_factory()
      end

      stringified_address = self.stringify_address(address: address)
      search = Geocoder.search(stringified_address)
      search_item = search[0]
      point = factory.point(
        search_item.data['lat'], search_item.data['lon']
      )

      UserActor.set_address(
        uuid: uuid,
        address: address,
        address_coordinate: point.to_s
      )
  end
end
