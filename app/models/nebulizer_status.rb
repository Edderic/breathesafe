# frozen_string_literal: true

class NebulizerStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    datetime = DateTime.now if datetime.nil?

    status = NebulizerStatusBuilder.build

    status.each_value do |v|
      v[:refresh_datetime] = datetime
      NebulizerStatus.create!(
        **v
      )
    end
  end
end
