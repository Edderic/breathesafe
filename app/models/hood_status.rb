# frozen_string_literal: true

class HoodStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    status = HoodStatusBuilder.build

    status.each_value do |row|
      row[:refresh_datetime] = datetime
      HoodStatus.create!(
        **row
      )
    end
  end
end
