# frozen_string_literal: true

require 'digest'

module MaskMatching
  class PredictionCache
    TTL = 24.hours

    def self.version
      # Remote model owners set this when publishing a new model. Inline changes
      # automatically invalidate classifications when the model or tokenizer changes.
      ENV['MASK_PREDICTOR_VERSION'].presence || artifact_version
    end

    def self.artifact_version
      @artifact_version ||= Digest::SHA256.hexdigest(
        %w[crf_model.pkl predict_inline.py].map do |file|
          path = Rails.root.join('python/mask_component_predictor', file)
          File.exist?(path) ? Digest::SHA256.file(path).hexdigest : 'missing'
        end.join(':')
      )
    end

    def self.key(name)
      "mask-matching/components/v1/#{version}/#{Digest::SHA256.hexdigest(name)}"
    end

    def self.read(name)
      Rails.cache.read(key(name))&.fetch(:components, nil)
    rescue StandardError
      nil
    end

    def self.read_many(names)
      keys = names.uniq.index_with { |name| key(name) }
      cached = Rails.cache.read_multi(*keys.values)
      keys.transform_values { |cache_key| cached[cache_key]&.fetch(:components, nil) }
    rescue StandardError
      {}
    end

    def self.predict(name)
      cached = Rails.cache.read(key(name))
      return cached[:components] if cached

      result = MaskComponentPredictorService.predict_with_timeout(name, seconds: 5)
      components = from_prediction(result)
      # Brief negative caching prevents repeated failures from spawning predictors.
      Rails.cache.write(key(name), { components: components }, expires_in: components ? TTL : 30.seconds)
      components
    rescue StandardError
      Rails.logger.warn('Mask classification cache unavailable; using name matching')
      nil
    end

    def self.from_prediction(result)
      return if result.blank? || result[:fallback]

      components = ComponentExtractor.from_breakdown(result[:breakdown])
      components if usable?(components)
    end

    def self.usable?(components)
      components.present? && (components[:brand].present? || components[:model].present?)
    end
  end
end
