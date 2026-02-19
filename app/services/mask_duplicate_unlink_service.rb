# frozen_string_literal: true

class MaskDuplicateUnlinkService
  class Error < StandardError; end

  class << self
    def call(mask_id:, user:, notes: nil)
      mask = Mask.find(mask_id)
      return build_result(mask, changed: false) if mask.duplicate_of.nil?

      MaskEvent.transaction do
        MaskEvent.create!(
          mask: mask,
          user: user,
          event_type: 'duplicate_marked',
          data: { 'duplicate_of' => nil },
          notes: notes.presence || 'Admin duplicate unlink'
        )
        mask.update!(MaskStatusBuilder.build_and_serialize(mask_id: mask.id))
      end

      build_result(mask.reload, changed: true)
    rescue ActiveRecord::RecordNotFound
      raise Error, 'Mask not found'
    rescue ActiveRecord::RecordInvalid => e
      raise Error, Array(e.record&.errors&.full_messages || e.message).to_sentence
    end

    private

    def build_result(mask, changed:)
      {
        mask_id: mask.id,
        duplicate_of: mask.duplicate_of,
        changed: changed
      }
    end
  end
end
