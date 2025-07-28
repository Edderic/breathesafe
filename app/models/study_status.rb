# frozen_string_literal: true

class StudyStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    statuses = StudyStatusBuilder.build

    statuses.each_value do |status|
      status['refresh_datetime'] = datetime
      StudyStatus.create!(**status)
    end
  end
end
