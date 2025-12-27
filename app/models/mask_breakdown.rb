# frozen_string_literal: true

class MaskBreakdown < ApplicationRecord
  belongs_to :mask
  belongs_to :user, class_name: 'User'

  validates :mask_id, presence: true
  validates :user_id, presence: true

  # Validate breakdown structure if present
  validate :validate_breakdown_structure, if: -> { breakdown.present? }

  # Get the latest breakdown for a mask
  scope :latest_for_mask, lambda { |mask_id|
    where(mask_id: mask_id).order(updated_at: :desc).limit(1)
  }

  # Check if breakdown is complete (all tokens are labeled)
  def complete?
    return false if breakdown.blank?

    breakdown.all? { |token_hash| token_hash.values.first.present? }
  end

  # Get list of tokens from mask's unique_internal_model_code
  def self.tokenize(unique_internal_model_code)
    return [] if unique_internal_model_code.blank?

    # Split by space, hyphen, em-dash, and comma
    # Keep the original tokens (don't downcase or strip yet)
    tokens = unique_internal_model_code.split(/[\s\-—,]+/)
    tokens.reject(&:blank?)
  end

  # Valid categories for token classification
  VALID_CATEGORIES = %w[
    brand
    model
    color
    style
    strap
    filter_type
    size
    misc
    valved
  ].freeze

  private

  def validate_breakdown_structure
    unless breakdown.is_a?(Array)
      errors.add(:breakdown, 'must be an array')
      return
    end

    breakdown.each_with_index do |item, index|
      unless item.is_a?(Hash)
        errors.add(:breakdown, "item at index #{index} must be a hash")
        next
      end

      if item.keys.length != 1
        errors.add(:breakdown, "item at index #{index} must have exactly one key")
        next
      end

      token = item.keys.first
      category = item.values.first

      errors.add(:breakdown, "token at index #{index} cannot be blank") if token.blank?

      if category.present? && !VALID_CATEGORIES.include?(category)
        errors.add(:breakdown,
                   "category '#{category}' at index #{index} is not valid. Must be one of: #{VALID_CATEGORIES.join(', ')}")
      end
    end
  end
end
