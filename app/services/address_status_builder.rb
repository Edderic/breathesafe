# frozen_string_literal: true

class AddressStatusBuilder
  def self.build
    actions = AddressAction.all.order(:datetime)
    actions.each_with_object({}) do |action, accum|
      metadata = action.metadata
      uuid = metadata['uuid']

      if action.name == 'CreateAddress'
        accum[uuid] = {}
        metadata_copy = JSON.parse(metadata.to_json)
        metadata_copy.delete('uuid')

        metadata_copy['address'].each do |k, v|
          accum[uuid][k] = v
        end
      end

      metadata_copy.delete('address')
      metadata_copy.each do |k, v|
        accum[uuid][k] = v
      end
    end
  end
end
