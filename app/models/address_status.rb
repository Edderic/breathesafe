class AddressStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    current_state = AddressStatusBuilder.build

    current_state.each do |uuid, data|
      data[:uuid] = uuid
      data[:refresh_datetime] = datetime
      self.create(**data)
    end
  end
end
