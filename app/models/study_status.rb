class StudyStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    statuses = StudyStatusBuilder.build

    statuses.each do |uuid, status|
      status['refresh_datetime'] = datetime
      StudyStatus.create!(**status)
    end
  end
end
