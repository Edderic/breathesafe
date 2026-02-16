# frozen_string_literal: true

# MaskEvent represents an append-only event log for mask changes
# Events are never updated or deleted, only added
class MaskEvent < ApplicationRecord
  belongs_to :mask
  belongs_to :user, class_name: 'User'

  validates :mask_id, presence: true
  validates :user_id, presence: true
  validates :event_type, presence: true
  validates :data, presence: true

  validate :validate_event_type
  validate :validate_data_structure

  # Valid event types
  VALID_EVENT_TYPES = %w[
    breakdown_updated
    color_changed
    colors_updated
    duplicate_marked
    perimeter_updated
    where_to_buy_urls_updated
    filtration_efficiencies_updated
    breathability_updated
    style_updated
    exhalation_valve_updated
    unique_internal_model_code_updated
    author_updated
    brand_updated
    strap_type_updated
    image_urls_updated
    mass_updated
    dimensions_updated
    gasket_updated
    cost_updated
    sources_updated
    modifications_updated
    notes_updated
    filter_type_updated
    age_range_updated
    payable_datetimes_updated
    bulk_import_updated
    availability_updated
  ].freeze

  # Get events for a mask in chronological order
  scope :for_mask, lambda { |mask_id|
    where(mask_id: mask_id).order(created_at: :asc)
  }

  # Get events up to a specific date
  scope :up_to_date, lambda { |date|
    where('created_at <= ?', date)
  }

  # Trigger mask regeneration after creating an event
  after_create :regenerate_mask_state

  private

  def validate_event_type
    return if VALID_EVENT_TYPES.include?(event_type)

    errors.add(:event_type, "must be one of: #{VALID_EVENT_TYPES.join(', ')}")
  end

  def validate_data_structure
    unless data.is_a?(Hash)
      errors.add(:data, 'must be a hash')
      return
    end

    # Event-specific validations can be added here
    case event_type
    when 'breakdown_updated'
      errors.add(:data, 'breakdown must be an array') unless data['breakdown'].is_a?(Array)
    when 'colors_updated'
      errors.add(:data, 'colors must be an array') unless data['colors'].is_a?(Array)
    when 'image_urls_updated'
      errors.add(:data, 'urls must be an array') unless data['urls'].is_a?(Array)
    end
  end

  def regenerate_mask_state
    # Trigger mask regeneration asynchronously to avoid blocking
    mask.regenerate
  rescue StandardError => e
    Rails.logger.error("Failed to regenerate mask #{mask_id}: #{e.message}")
  end
end
