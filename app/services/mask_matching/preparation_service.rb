# frozen_string_literal: true

module MaskMatching
  # Prepares all the data needed for mask matching:
  # - From-file breakdown predictions (cached on the bulk import)
  # - Catalog mask breakdowns (from mask events or predictor fallback)
  # - Weighted similarity scores between each pair
  class PreparationService
    BATCH_SIZE = 25

    attr_reader :bulk_import, :mask_names, :current_user

    def initialize(bulk_import:, mask_names:, current_user:)
      @bulk_import = bulk_import
      @mask_names = Array(mask_names).map(&:to_s).reject(&:blank?).uniq
      @current_user = current_user
      @from_file_cache = (bulk_import.from_file_mask_breakdowns || {}).dup
      @from_file_errors = (bulk_import.from_file_mask_breakdown_errors || {}).dup
      @cache_changed = false
    end

    def call
      ensure_from_file_breakdowns!
      catalog = build_catalog_data
      recommendations = build_recommendations(catalog)

      {
        from_file_masks: @from_file_cache,
        catalog_masks: catalog.values,
        recommendations: recommendations,
        component_weights: MaskMatching::Scorer::COMPONENT_WEIGHTS,
        auto_match_threshold: MaskMatching::Scorer::AUTO_MATCH_THRESHOLD,
        errors: @from_file_errors
      }
    end

    private

    def ensure_from_file_breakdowns!
      names_to_predict = mask_names.reject do |name|
        @from_file_cache.key?(name) && @from_file_cache[name].present?
      end

      names_to_predict.each_slice(BATCH_SIZE) do |batch|
        predictions = predict_batch(batch)
        batch.each_with_index do |mask_name, idx|
          result = predictions[idx]

          if result.blank? || result[:fallback]
            mark_prediction_error(mask_name, 'Prediction unavailable')
            next
          end

          store_prediction(mask_name, result)
        end
      end

      persist_cache! if @cache_changed
    end

    def predict_batch(batch)
      MaskComponentPredictorService.predict_batch(batch)
    rescue StandardError => e
      Rails.logger.error("Mask predictor batch failed: #{e.message}")
      batch.map { |_| nil }
    end

    def mark_prediction_error(mask_name, message)
      return if mask_name.blank?

      @from_file_errors[mask_name] = message
      @cache_changed = true
    end

    def store_prediction(mask_name, result)
      breakdown = result[:breakdown]
      components = MaskMatching::ComponentExtractor.from_breakdown(breakdown)

      @from_file_cache[mask_name] = {
        'mask_name' => mask_name,
        'breakdown' => breakdown,
        'components' => components.transform_values { |tokens| tokens.map(&:dup) },
        'confidence' => result[:confidence],
        'source' => 'predictor',
        'predicted_at' => Time.current.iso8601
      }
      @from_file_errors.delete(mask_name)
      @cache_changed = true
    end

    def persist_cache!
      bulk_import.update!(
        from_file_mask_breakdowns: @from_file_cache,
        from_file_mask_breakdown_errors: @from_file_errors
      )
    end

    def build_catalog_data
      masks = Mask.where(duplicate_of: nil)
                  .includes(:brand)
                  .order(:unique_internal_model_code)

      masks.each_with_object({}) do |mask, acc|
        breakdown, source = catalog_breakdown_for(mask)
        components = MaskMatching::ComponentExtractor.from_breakdown(breakdown)
        components = MaskMatching::ComponentExtractor.enrich_with_mask_attributes(components, mask)

        acc[mask.id] = {
          id: mask.id,
          unique_internal_model_code: mask.unique_internal_model_code,
          brand_name: mask.brand&.name,
          breakdown: breakdown,
          components: components,
          source: source,
          duplicate_of: mask.duplicate_of
        }
      end
    end

    def catalog_breakdown_for(mask)
      breakdown = mask.current_state&.dig('breakdown')
      return [breakdown, 'current_state'] if breakdown.present?

      latest_event = mask.mask_events
                         .where(event_type: 'breakdown_updated')
                         .order(created_at: :desc)
                         .limit(1)
                         .first
      return [latest_event&.data&.fetch('breakdown', nil), 'event'] if latest_event&.data&.key?('breakdown')

      prediction = MaskComponentPredictorService.predict(mask.unique_internal_model_code)
      return [prediction[:breakdown], 'predicted'] if prediction && !prediction[:fallback]

      [[], 'unavailable']
    rescue StandardError => e
      Rails.logger.error("Unable to fetch breakdown for mask #{mask.id}: #{e.message}")
      [[], 'unavailable']
    end

    def build_recommendations(catalog)
      return {} if @from_file_cache.blank?

      recommendations = {}

      @from_file_cache.each do |mask_name, payload|
        next if payload.blank?

        components = payload['components'] || {}
        next if components.blank?

        scores = catalog.values.filter_map do |catalog_mask|
          next if catalog_mask[:components].blank?

          comparison = MaskMatching::Scorer.score(components, catalog_mask[:components])
          score = comparison[:score]
          next if score.zero?

          {
            mask_id: catalog_mask[:id],
            mask_name: catalog_mask[:unique_internal_model_code],
            score: score,
            component_scores: comparison[:component_scores]
          }
        end

        next if scores.blank?

        scores.sort_by! { |entry| -entry[:score] }
        recommendations[mask_name] = scores.first(5).map do |entry|
          entry.merge(score: entry[:score].round(4))
        end
      end

      recommendations
    end
  end
end
