# frozen_string_literal: true

module MaskMatching
  # Utility methods for converting breakdown arrays into component hashes
  class ComponentExtractor
    COMPONENT_KEYS = %i[
      brand
      model
      filter_type
      size
      strap
      style
      color
      valved
      misc
    ].freeze

    class << self
      def from_breakdown(breakdown)
        components = COMPONENT_KEYS.index_with { [] }

        Array(breakdown).each do |entry|
          token, label = entry.is_a?(Hash) ? entry.first : entry
          next if token.blank? || label.blank?

          key = normalize_label(label)
          next unless components.key?(key)

          components[key] << token.to_s
        end

        components
      end

      def enrich_with_mask_attributes(components, mask)
        return components unless mask

        copy = deep_dup_components(components)

        if copy[:filter_type].blank? && mask.filter_type.present?
          copy[:filter_type] = attribute_tokens(mask.filter_type)
        end
        copy[:strap] = attribute_tokens(mask.strap_type) if copy[:strap].blank? && mask.strap_type.present?
        copy[:style] = attribute_tokens(mask.style) if copy[:style].blank? && mask.style.present?

        copy
      end

      private

      def normalize_label(label)
        case label.to_s.downcase
        when 'brand'
          :brand
        when 'model'
          :model
        when 'filter_type', 'filter'
          :filter_type
        when 'size'
          :size
        when 'strap', 'strap_type'
          :strap
        when 'style'
          :style
        when 'color', 'colour'
          :color
        when 'valved', 'valve'
          :valved
        else
          :misc
        end
      end

      def attribute_tokens(value)
        value.to_s.split(%r{[/,]+}).map(&:strip).reject(&:blank?)
      end

      def deep_dup_components(components)
        COMPONENT_KEYS.index_with do |key|
          Array(components[key]).map(&:dup)
        end
      end
    end
  end
end
