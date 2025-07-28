# frozen_string_literal: true

class MaskKitStatus < ApplicationRecord
  def self.refresh!(datetime: nil, uuid: nil)
    datetime = DateTime.now if datetime.nil?

    # TODO: builders could take in the datetime, and only build up to that
    # datetime.
    # This could let us see the statuses over time
    results = MaskKitStatusBuilder.build(uuid: uuid)

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
