# frozen_string_literal: true

class MaskDeduplicationPolicy
  class << self
    def root_scope(scope = Mask.all)
      scope.where(duplicate_of: nil)
    end

    def canonicalize_mask_ids(mask_ids)
      return [] if mask_ids.blank?

      mapping = canonical_ids_by_mask_id(mask_ids)
      mask_ids.filter_map { |mask_id| mapping[mask_id.to_i] || mask_id.to_i }.uniq
    end

    def canonical_ids_by_mask_id(mask_ids)
      ids = Array(mask_ids).filter_map { |mask_id| integer_id(mask_id) }.uniq
      return {} if ids.empty?

      duplicate_of_by_id = Mask.pluck(:id, :duplicate_of).to_h
      ids.index_with { |mask_id| canonical_id_for(mask_id, duplicate_of_by_id) }
    end

    private

    def canonical_id_for(mask_id, duplicate_of_by_id)
      current = mask_id
      visited = Set.new

      while current.present? && duplicate_of_by_id.key?(current)
        break if visited.include?(current)

        visited << current
        parent = duplicate_of_by_id[current]
        break if parent.blank?

        current = parent
      end

      current
    end

    def integer_id(value)
      Integer(value)
    rescue ArgumentError, TypeError
      nil
    end
  end
end
