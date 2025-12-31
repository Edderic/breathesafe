# frozen_string_literal: true

class MaskPair < ApplicationRecord
  belongs_to :mask_a, class_name: 'Mask', inverse_of: :mask_pairs_as_a
  belongs_to :mask_b, class_name: 'Mask', inverse_of: :mask_pairs_as_b

  validates :name_distance, presence: true
  validates :mask_a_id, uniqueness: { scope: :mask_b_id, message: 'pair already exists' }
  validate :mask_a_id_less_than_mask_b_id
  validate :history_is_array

  # Ensure pairs are always stored with mask_a_id < mask_b_id for consistency
  before_validation :normalize_pair_order

  private

  def normalize_pair_order
    return unless mask_a_id.present? && mask_b_id.present?

    # Swap if mask_a_id > mask_b_id to ensure consistent ordering
    self.mask_a_id, self.mask_b_id = mask_b_id, mask_a_id if mask_a_id > mask_b_id
  end

  def mask_a_id_less_than_mask_b_id
    return unless mask_a_id.present? && mask_b_id.present?

    return if mask_a_id < mask_b_id

    errors.add(:base, 'mask_a_id must be less than mask_b_id')
  end

  def history_is_array
    return if history.is_a?(Array)

    errors.add(:history, 'must be an array')
  end
end
