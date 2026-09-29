# frozen_string_literal: true

module MaskMatching
  class CatalogComponents
    def self.call(masks)
      ids = masks.map(&:id)
      # One query, not one per mask. Respect annotations even when they are empty:
      # do not silently replace an admin's breakdown with a prediction.
      events = MaskEvent.where(mask_id: ids, event_type: 'breakdown_updated')
                        .order(:mask_id, created_at: :desc, id: :desc)
                        .pluck(:mask_id, :data).each_with_object({}) do |(id, data), rows|
        rows[id] = data['breakdown'] if !rows.key?(id) && data.key?('breakdown')
      end
      predictions = PredictionCache.read_many(masks.map { |mask| mask.unique_internal_model_code.to_s })
      missing = []
      result = masks.to_h do |mask|
        breakdown = if mask.current_state&.key?('breakdown')
                      mask.current_state['breakdown']
                    else
                      events[mask.id]
                    end
        components = if breakdown.nil?
                       predictions[mask.unique_internal_model_code.to_s]
                     else
                       ComponentExtractor.from_breakdown(breakdown)
                     end
        missing << mask.id if components.nil? && breakdown.nil?
        components = ComponentExtractor.enrich_with_mask_attributes(components, mask) if components
        [mask.id, components]
      end
      schedule(missing) if missing.any?
      result
    end

    def self.schedule(ids)
      key = "mask-matching/warm/v1/#{PredictionCache.version}"
      return unless Rails.cache.write(key, true, unless_exist: true, expires_in: 5.minutes)

      WarmMaskMatchingCatalogJob.perform_later(ids)
    rescue StandardError
      Rails.logger.warn('Could not schedule catalog classifications; using name matching')
    end
  end
end
