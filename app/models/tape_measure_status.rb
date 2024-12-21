class TapeMeasureStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    statuses = TapeMeasureStatusBuilder.build

    statuses.each do |uuid, status|
      status['refresh_datetime'] = datetime
      TapeMeasureStatus.create!(**status)
    end
  end
end
