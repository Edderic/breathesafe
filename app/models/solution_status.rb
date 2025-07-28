# frozen_string_literal: true

class SolutionStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

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
