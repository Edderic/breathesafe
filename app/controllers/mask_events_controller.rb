# frozen_string_literal: true

class MaskEventsController < ApplicationController
  before_action :authenticate_user!
  before_action :require_admin!

  # GET /masks/:mask_id/events.json
  # Returns event history for a mask
  def index
    mask = Mask.find(params[:mask_id])
    events = MaskEvent.where(mask_id: mask.id)
                      .order(created_at: :desc)
                      .includes(:user)

    events_data = events.map do |event|
      {
        id: event.id,
        event_type: event.event_type,
        data: event.data,
        notes: event.notes,
        created_at: event.created_at,
        updated_at: event.updated_at,
        user: {
          id: event.user.id,
          email: event.user.email
        }
      }
    end

    render json: {
      mask_id: mask.id,
      unique_internal_model_code: mask.unique_internal_model_code,
      events: events_data,
      total_count: events.count
    }
  end

  private

  def require_admin!
    return if current_user&.admin?

    render json: { error: 'Unauthorized. Admin access required.' }, status: :forbidden
  end
end
