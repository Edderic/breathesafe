# frozen_string_literal: true

class AddressStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    current_state = AddressStatusBuilder.build

    current_state.each do |uuid, data|
      data[:uuid] = uuid
      data[:refresh_datetime] = datetime
      create!(**data)
    end
  end
end
