# frozen_string_literal: true

class MaskDuplicateChainFlattener
  class Error < StandardError; end

  class << self
    def call(apply: false, user: nil, notes_prefix: 'Admin duplicate chain flatten')
      duplicate_rows = Mask.where.not(duplicate_of: nil).pluck(:id, :duplicate_of)
      mask_ids = duplicate_rows.map(&:first)
      canonical_by_mask_id = MaskDeduplicationPolicy.canonical_ids_by_mask_id(mask_ids)

      plan = duplicate_rows.filter_map do |mask_id, duplicate_of|
        canonical_root_id = canonical_by_mask_id[mask_id]
        next if canonical_root_id.blank?
        next if canonical_root_id == mask_id
        next if duplicate_of == canonical_root_id

        {
          mask_id: mask_id,
          current_duplicate_of: duplicate_of,
          canonical_root_id: canonical_root_id
        }
      end

      result = {
        apply: apply,
        total_duplicates: duplicate_rows.size,
        flatten_candidates: plan.size,
        planned: plan,
        changed: [],
        errors: []
      }

      return result unless apply

      raise Error, 'A user is required when apply=true' unless user

      plan.each do |entry|
        MaskDuplicateLinkService.call(
          child_mask_id: entry[:mask_id],
          target_mask_id: entry[:canonical_root_id],
          user: user,
          notes: "#{notes_prefix}: previous_duplicate_of=#{entry[:current_duplicate_of]}"
        )
        result[:changed] << entry
      rescue StandardError => e
        result[:errors] << entry.merge(error: e.message)
      end

      result
    end
  end
end
