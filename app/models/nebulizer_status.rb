class NebulizerStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    status = NebulizerStatusBuilder.build

    status.each do |uuid, v|
      v[:refresh_datetime] = datetime
      NebulizerStatus.create!(
        **v
      )

    end
  end
end
