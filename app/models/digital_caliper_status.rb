class DigitalCaliperStatus < ApplicationRecord
  def self.refresh!(datetime:nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    rows = DigitalCaliperStatusBuilder.build

    rows.each do |uuid, row|
      row[:uuid] = uuid
      row[:refresh_datetime] = datetime
      DigitalCaliperStatus.create!(**row)
    end
  end
end
