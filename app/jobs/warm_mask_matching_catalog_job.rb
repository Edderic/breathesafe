# frozen_string_literal: true

class WarmMaskMatchingCatalogJob < ApplicationJob
  def perform(ids)
    Mask.where(id: ids, duplicate_of: nil).find_each do |mask|
      next if mask.current_state&.key?('breakdown')
      next if mask.mask_events.where(event_type: 'breakdown_updated').exists?

      MaskMatching::PredictionCache.predict(mask.unique_internal_model_code.to_s)
    end
  end
end
