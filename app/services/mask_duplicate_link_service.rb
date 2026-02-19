# frozen_string_literal: true

class MaskDuplicateLinkService
  class Error < StandardError; end

  class << self
    def call(child_mask_id:, target_mask_id:, user:, notes: nil)
      child_mask = Mask.find(child_mask_id)
      canonical_target_mask_id = MaskDeduplicationPolicy.canonicalize_mask_ids([target_mask_id]).first

      raise Error, 'Target mask is required' if canonical_target_mask_id.blank?
      raise Error, 'A mask cannot be marked as a duplicate of itself' if child_mask.id == canonical_target_mask_id

      if child_mask.duplicate_of == canonical_target_mask_id
        return build_result(child_mask, canonical_target_mask_id,
                            changed: false)
      end

      MaskEvent.transaction do
        MaskEvent.create!(
          mask: child_mask,
          user: user,
          event_type: 'duplicate_marked',
          data: { 'duplicate_of' => canonical_target_mask_id },
          notes: notes.presence || 'Admin duplicate link'
        )
        child_mask.update!(MaskStatusBuilder.build_and_serialize(mask_id: child_mask.id))
      end

      build_result(child_mask.reload, canonical_target_mask_id, changed: true)
    rescue ActiveRecord::RecordNotFound
      raise Error, 'Mask not found'
    rescue ActiveRecord::RecordInvalid => e
      raise Error, Array(e.record&.errors&.full_messages || e.message).to_sentence
    end

    private

    def build_result(mask, canonical_target_mask_id, changed:)
      {
        mask_id: mask.id,
        duplicate_of: mask.duplicate_of,
        canonical_target_mask_id: canonical_target_mask_id,
        changed: changed
      }
    end
  end
end
