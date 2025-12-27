# frozen_string_literal: true

# MaskStatusBuilder replays events to compute the current state of a mask
class MaskStatusBuilder
  attr_reader :mask_id, :as_of_date

  def initialize(mask_id:, as_of_date: Time.current)
    @mask_id = mask_id
    @as_of_date = as_of_date
  end

  # Build and return a MaskStatus object
  def call
    status = MaskStatus.new(mask_id: mask_id, as_of_date: as_of_date)

    # Step 1: Get the initial state
    initial_state = MaskState.initial_for_mask(mask_id).first

    if initial_state
      status.apply_initial_state(initial_state)
    else
      # If no initial state exists, start with empty attributes
      Rails.logger.warn("No initial state found for mask #{mask_id}")
    end

    # Step 2: Get all events up to the as_of_date in chronological order
    events = MaskEvent.for_mask(mask_id).up_to_date(as_of_date)

    # Step 3: Apply each event in order
    events.each do |event|
      status.apply_event(event)
    end

    status
  end

  # Convenience method to build and serialize in one call
  def self.build_and_serialize(mask_id:, as_of_date: Time.current)
    new(mask_id: mask_id, as_of_date: as_of_date).call.serialize
  end
end
