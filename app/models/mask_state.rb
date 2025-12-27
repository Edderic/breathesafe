# frozen_string_literal: true

# MaskState represents a snapshot of a mask's state at a specific point in time
# This is typically the initial state when a mask is first created
class MaskState < ApplicationRecord
  belongs_to :mask
  belongs_to :author, class_name: 'User', optional: true
  belongs_to :brand, optional: true
  belongs_to :bulk_fit_tests_import, optional: true

  validates :mask_id, presence: true

  # Get the initial state for a mask
  scope :initial_for_mask, lambda { |mask_id|
    where(mask_id: mask_id).order(created_at: :asc).limit(1)
  }

  # Convert this state to a hash suitable for updating a Mask
  def to_mask_attributes
    attributes.except('id', 'mask_id', 'created_at', 'updated_at').compact
  end
end
