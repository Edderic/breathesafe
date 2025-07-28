# frozen_string_literal: true

class FacialMeasurementKitStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    statuses = FacialMeasurementKitStatusBuilder.build

    statuses.each_key do |uuid|
      FacialMeasurementKitStatus.create!(
        uuid: uuid,
        refresh_datetime: datetime
      )
    end
  end
end
