# frozen_string_literal: true

module MaskMatching
  # Scores how well a from-file mask matches an existing catalog mask
  class Scorer
    COMPONENT_WEIGHTS = {
      brand: 0.45,
      model: 0.30,
      filter_type: 0.08,
      size: 0.08,
      strap: 0.05,
      style: 0.04
    }.freeze

    AUTO_MATCH_THRESHOLD = 0.5

    KID_KEYWORDS = %w[kid kids child children youth toddler tween infant junior teen].freeze
    ADULT_KEYWORDS = %w[adult men womens women's mens unisex].freeze

    SIZE_PATTERNS = {
      xlarge: [/extra[\s-]?large/, /\bxl\b/, /\b2xl\b/, /\bxxl\b/],
      large: [/\blarge\b/, /\blg\b/, /\bl\b(?![a-z])/],
      medium: [/\bmedium\b/, /\bmed\b/, /\bmd\b/, /\bregular\b/],
      small: [/\bsmall\b/, /\bsm\b/, /\bs\b(?![a-z])/],
      petite: [/petite/]
    }.freeze

    BRAND_HINTS = {
      /aura\s?92\d+/ => '3m',
      /\b3m\b/ => '3m',
      /can99/ => 'vitacore',
      /vitacore/ => 'vitacore',
      /wellbefore/ => 'wellbefore',
      /laianzhi/ => 'laianzhi',
      /hyx1002/ => 'laianzhi',
      /readimask/ => 'readimask',
      /medimask/ => 'medimask'
    }.freeze

    class << self
      def score(file_components, mask_components)
        file_components = deep_dup_components(symbolize_component_keys(file_components))
        mask_components = deep_dup_components(symbolize_component_keys(mask_components))

        backfill_brand_from_model!(file_components)
        backfill_brand_from_model!(mask_components)

        file_age_group = detect_age_group(file_components, default: :adult)
        mask_age_group = detect_age_group(mask_components)
        file_size = detect_size(file_components)
        mask_size = detect_size(mask_components)

        details = {}
        weighted_total = 0.0
        applied_weight = 0.0

        COMPONENT_WEIGHTS.each do |component, weight|
          detail = component_similarity(component,
                                        Array(file_components[component]),
                                        Array(mask_components[component]))
          details[component] = detail

          next if detail[:weightless]

          weighted_total += detail[:score] * weight
          applied_weight += weight
        end

        base_score = applied_weight.zero? ? 0.0 : weighted_total / applied_weight

        brand_score = details.dig(:brand, :score) || 0.0
        model_score = details.dig(:model, :score) || 0.0

        final_score = base_score

        if brand_present?(file_components) && brand_present?(mask_components) && brand_score < 0.95
          final_score *= brand_score
        end

        if model_present?(file_components) && model_present?(mask_components) && model_score < 0.5
          final_score *= model_score
        end

        if conflicting_age_group?(file_age_group, mask_age_group)
          final_score *= 0.05
        end

        if conflicting_size?(file_size, mask_size)
          final_score *= 0.1
        end

        {
          score: final_score.clamp(0.0, 1.0),
          component_scores: details
        }
      end

      private

      def component_similarity(component, file_tokens, mask_tokens)
        cleaned_file_tokens = normalize_tokens(component, file_tokens)
        cleaned_mask_tokens = normalize_tokens(component, mask_tokens)

        if cleaned_file_tokens.empty? && cleaned_mask_tokens.empty?
          return {
            score: 0.0,
            weightless: true,
            pairs: [],
            file_tokens: file_tokens || [],
            mask_tokens: mask_tokens || []
          }
        end

        if cleaned_file_tokens.empty? || cleaned_mask_tokens.empty?
          return {
            score: 0.0,
            weightless: false,
            pairs: [],
            file_tokens: file_tokens || [],
            mask_tokens: mask_tokens || []
          }
        end

        matches = match_tokens(component, cleaned_file_tokens, cleaned_mask_tokens)
        denominator = [cleaned_file_tokens.length, cleaned_mask_tokens.length].max
        similarity = matches.sum { |match| match[:score] }.fdiv(denominator)

        {
          score: similarity.clamp(0.0, 1.0),
          weightless: false,
          pairs: matches,
          file_tokens: file_tokens || [],
          mask_tokens: mask_tokens || []
        }
      end

      def normalize_tokens(component, tokens)
        Array(tokens).map do |token|
          token = token.to_s.strip
          next if token.blank?

          normalized = token.downcase
          normalized = normalized.gsub(/[^a-z0-9+-]/, ' ')
                                 .gsub(/\s+/, ' ')
                                 .strip

          {
            raw: token,
            normalized: normalized,
            component: component
          }
        end.compact
      end

      def match_tokens(component, source_tokens, target_tokens)
        matches = []
        used_target_indexes = []

        source_tokens.each do |source_token|
          best = { score: 0.0, token: nil, index: nil }

          target_tokens.each_with_index do |target_token, idx|
            next if used_target_indexes.include?(idx)

            similarity = token_similarity(component,
                                          source_token[:normalized],
                                          target_token[:normalized])
            next unless similarity > best[:score]

            best = { score: similarity, token: target_token, index: idx }
          end

          if best[:token]
            used_target_indexes << best[:index]
            matches << {
              file_token: source_token[:raw],
              mask_token: best[:token][:raw],
              score: best[:score].clamp(0.0, 1.0)
            }
          else
            matches << {
              file_token: source_token[:raw],
              mask_token: nil,
              score: 0.0
            }
          end
        end

        # Include any remaining catalog tokens that were not matched
        target_tokens.each_with_index do |target_token, idx|
          next if used_target_indexes.include?(idx)

          matches << {
            file_token: nil,
            mask_token: target_token[:raw],
            score: 0.0
          }
        end

        matches
      end

      def token_similarity(component, source, target)
        return 1.0 if source == target

        if component == :model
          base_source = source.gsub(/[-_]?0*\d+\z/, '')
          base_target = target.gsub(/[-_]?0*\d+\z/, '')
          return 0.9 if base_source.present? && base_source == base_target
        end

        max_length = [source.length, target.length].max
        return 0.0 if max_length.zero?

        1.0 - levenshtein_distance(source, target).fdiv(max_length)
      end

      def levenshtein_distance(str1, str2)
        m = str1.length
        n = str2.length
        return n if m.zero?
        return m if n.zero?

        matrix = Array.new(m + 1) { Array.new(n + 1, 0) }
        (0..m).each { |i| matrix[i][0] = i }
        (0..n).each { |j| matrix[0][j] = j }

        (1..m).each do |i|
          (1..n).each do |j|
            cost = str1[i - 1] == str2[j - 1] ? 0 : 1
            matrix[i][j] = [
              matrix[i - 1][j] + 1,     # deletion
              matrix[i][j - 1] + 1,     # insertion
              matrix[i - 1][j - 1] + cost # substitution
            ].min
          end
        end

        matrix[m][n]
      end

      def symbolize_component_keys(components)
        return {} if components.blank?

        components.each_with_object({}) do |(key, value), acc|
          sym_key = key.respond_to?(:to_sym) ? key.to_sym : key
          acc[sym_key] = value
        end
      end

      def deep_dup_components(components)
        components.each_with_object({}) do |(key, value), acc|
          acc[key] = value.is_a?(Array) ? value.map(&:dup) : value
        end
      end

      def backfill_brand_from_model!(components)
        return if brand_present?(components)

        inferred = infer_brand_from_tokens(components)
        return if inferred.blank?

        components[:brand] ||= []
        components[:brand] << inferred
      end

      def infer_brand_from_tokens(components)
        tokens = flattened_tokens(components)
        BRAND_HINTS.each do |regex, brand|
          return brand if tokens.any? { |token| token.match?(regex) }
        end
        nil
      end

      def detect_age_group(components, default: nil)
        tokens = flattened_tokens(components)
        return :kids if tokens.any? { |token| KID_KEYWORDS.any? { |kw| token.include?(kw) } }
        return :adult if tokens.any? { |token| ADULT_KEYWORDS.any? { |kw| token.include?(kw) } }

        default
      end

      def detect_size(components)
        tokens = flattened_tokens(components)
        SIZE_PATTERNS.each do |size, patterns|
          return size if tokens.any? { |token| patterns.any? { |regex| token.match?(regex) } }
        end
        nil
      end

      def flattened_tokens(components)
        components
          .values
          .flat_map { |value| Array(value) }
          .compact
          .map { |token| token.to_s.downcase }
      end

      def brand_present?(components)
        Array(components[:brand]).any?(&:present?)
      end

      def model_present?(components)
        Array(components[:model]).any?(&:present?)
      end

      def conflicting_age_group?(file_group, mask_group)
        return false if file_group.nil? || mask_group.nil?

        file_group != mask_group
      end

      def conflicting_size?(file_size, mask_size)
        return false if file_size.nil? || mask_size.nil?

        file_size != mask_size
      end
    end
  end
end
