# frozen_string_literal: true

class TapeMeasureStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    statuses = TapeMeasureStatusBuilder.build

    statuses.each_value do |status|
      status['refresh_datetime'] = datetime
      TapeMeasureStatus.create!(**status)
    end
  end
end
