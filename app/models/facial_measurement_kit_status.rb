class FacialMeasurementKitStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    statuses = FacialMeasurementKitStatusBuilder.build

    statuses.each do |uuid, status|
      FacialMeasurementKitStatus.create!(
        uuid: uuid,
        refresh_datetime: datetime
      )
    end
  end
end
