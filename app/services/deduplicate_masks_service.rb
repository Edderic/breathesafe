# frozen_string_literal: true

class DeduplicateMasksService
  class << self
    def call(from_mask_id:, to_mask_id:)
      fit_tests = FitTest.where(mask_id: from_mask_id)

      ActiveRecord::Base.transaction do
        fit_tests.each do |fit_test|
          fit_test.update(mask_id: to_mask_id)
        end

        MaskKitStatus.destroy_all
        MaskKitStatus.refresh!

        mask_kit_statuses = MaskKitStatus.where(mask_uuid: from_mask_id)
        mask_kit_statuses.each do |mks|
          MaskKitActor.update_mask_id(
            uuid: mks.uuid,
            from_mask_uuid: from_mask_id,
            to_mask_uuid: to_mask_id
          )
        end

        MaskKitStatus.destroy_all
        MaskKitStatus.refresh!

        mask_to_destroy = Mask.find(from_mask_id)
        # saveable_mask = Mask.find(to_mask_id)
        # debugger

        mask_to_destroy.destroy
      end
    end
  end
end
