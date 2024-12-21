class MaskKitStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    results = MaskKitStatusBuilder.build

    results.each do |uuid, details|
      details['mask_uuids'].each do |mask_uuid|
        MaskKitStatus.create(
          uuid: uuid,
          mask_uuid: mask_uuid,
          refresh_datetime: datetime
        )
      end
    end
  end
end
