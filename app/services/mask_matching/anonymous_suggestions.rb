# frozen_string_literal: true

module MaskMatching
  class AnonymousSuggestions
    def self.call(name)
      masks = Mask.where(duplicate_of: nil)
                  .select(:id, :unique_internal_model_code, :current_state, :filter_type, :strap_type, :style).to_a
      catalog = CatalogComponents.call(masks)
      source = PredictionCache.predict(name)
      scores = masks.filter_map do |mask|
        target = catalog[mask.id]
        comparison = if PredictionCache.usable?(source) && PredictionCache.usable?(target)
                       # Exclude color from both weighting and size/age detection.
                       Scorer.score(source.except(:color), target.except(:color))
                     else
                       Scorer.score(components(name), components(mask.unique_internal_model_code))
                     end
        score = comparison[:score]
        next if score < 0.25

        { id: mask.id, name: mask.unique_internal_model_code, score: score.round(4) }
      end
      scores.sort_by { |row| [-row[:score], row[:id]] }.first(5)
    end

    def self.components(name)
      { model: name.to_s.downcase.scan(/[[:alnum:]+]+/) }
    end
  end
end
