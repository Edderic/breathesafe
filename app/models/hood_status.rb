class HoodStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    status = HoodStatusBuilder.build

    status.each do |uuid, row|
      row[:refresh_datetime] = datetime
      HoodStatus.create!(
        **row
      )
    end
  end
end
