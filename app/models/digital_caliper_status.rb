# frozen_string_literal: true

class DigitalCaliperStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    rows = DigitalCaliperStatusBuilder.build

    rows.each do |uuid, row|
      row[:uuid] = uuid
      row[:refresh_datetime] = datetime
      DigitalCaliperStatus.create!(**row)
    end
  end
end
