class SolutionStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    status = SolutionStatusBuilder.build

    status.each do |uuid, v|
      v['refresh_datetime'] = datetime
      v['uuid'] = uuid

      SolutionStatus.create!(
        **v
      )
    end
  end
end
