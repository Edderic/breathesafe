# frozen_string_literal: true

module MaskMatching
  # Reuse the import scorer without exposing predictor infrastructure to a public
  # endpoint. Token comparisons handle spelling differences and size conflicts;
  # suggestions always require a person's confirmation, including exact names.
  class AnonymousSuggestions
    def self.call(name)
      source = components(name)
      scores = Mask.where(duplicate_of: nil).pluck(:id, :unique_internal_model_code).filter_map do |id, label|
        score = Scorer.score(source, components(label))[:score]
        next if score < 0.25

        { id: id, name: label, score: score.round(4) }
      end
      scores.sort_by { |row| [-row[:score], row[:id]] }.first(5)
    end

    def self.components(name)
      { model: name.to_s.downcase.scan(/[[:alnum:]+]+/) }
    end
  end
end
