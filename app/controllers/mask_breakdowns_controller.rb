# frozen_string_literal: true

class MaskBreakdownsController < ApplicationController
  include MaskTokenizer

  before_action :authenticate_user!
  before_action :require_admin!

  # GET /mask_breakdowns.json
  # Returns all masks with their latest breakdown (if any)
  def index
    masks = Mask.order(:unique_internal_model_code)
                .select(:id, :unique_internal_model_code)
                .to_a

    # Get latest breakdown event for each mask
    mask_data = masks.map do |mask|
      latest_event = MaskEvent.where(mask_id: mask.id, event_type: 'breakdown_updated')
                              .order(created_at: :desc)
                              .limit(1)
                              .first

      tokens = MaskTokenizer.tokenize(mask.unique_internal_model_code)
      breakdown = latest_event&.data&.dig('breakdown') || []

      {
        id: mask.id,
        unique_internal_model_code: mask.unique_internal_model_code,
        tokens: tokens,
        breakdown: breakdown,
        breakdown_id: latest_event&.id,
        breakdown_complete: breakdown.present? && breakdown.all? { |item| item.values.first.present? },
        breakdown_updated_at: latest_event&.updated_at,
        breakdown_user: if latest_event&.user
                          {
                            id: latest_event.user.id,
                            email: latest_event.user.email
                          }
                        end
      }
    end

    render json: {
      masks: mask_data,
      total_count: masks.length,
      completed_count: mask_data.count { |m| m[:breakdown_complete] },
      categories: MaskTokenizer::VALID_CATEGORIES
    }
  end

  # GET /mask_breakdowns/:id.json
  # Returns a specific mask with its breakdown
  def show
    mask = Mask.find(params[:id])
    latest_event = MaskEvent.where(mask_id: mask.id, event_type: 'breakdown_updated')
                            .order(created_at: :desc)
                            .limit(1)
                            .first

    tokens = MaskTokenizer.tokenize(mask.unique_internal_model_code)
    breakdown = latest_event&.data&.dig('breakdown') || []

    render json: {
      id: mask.id,
      unique_internal_model_code: mask.unique_internal_model_code,
      tokens: tokens,
      breakdown: breakdown,
      breakdown_id: latest_event&.id,
      breakdown_complete: breakdown.present? && breakdown.all? { |item| item.values.first.present? },
      breakdown_updated_at: latest_event&.updated_at,
      breakdown_user: if latest_event&.user
                        {
                          id: latest_event.user.id,
                          email: latest_event.user.email
                        }
                      end,
      categories: MaskTokenizer::VALID_CATEGORIES
    }
  end

  # POST /mask_breakdowns.json
  # Creates a breakdown event for a mask
  def create
    mask = Mask.find(params[:mask_id])
    breakdown_data = params[:breakdown] || []

    # Create a breakdown_updated event
    mask_event = MaskEvent.new(
      mask: mask,
      user: current_user,
      event_type: 'breakdown_updated',
      data: { breakdown: breakdown_data },
      notes: params[:notes]
    )

    if mask_event.save
      # The after_create callback on MaskEvent will trigger mask.regenerate
      render json: {
        success: true,
        breakdown: {
          id: mask_event.id,
          mask_id: mask_event.mask_id,
          breakdown: breakdown_data,
          complete: breakdown_data.all? { |item| item.values.first.present? },
          updated_at: mask_event.updated_at,
          user: {
            id: mask_event.user.id,
            email: mask_event.user.email
          }
        }
      }, status: :created
    else
      render json: {
        success: false,
        errors: mask_event.errors.full_messages
      }, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /mask_breakdowns/:id.json
  # Creates a new breakdown event (append-only, never updates)
  def update
    # Find the previous event to get the mask
    previous_event = MaskEvent.find(params[:id])
    breakdown_data = params[:breakdown] || []

    # Create a new breakdown_updated event
    mask_event = MaskEvent.new(
      mask: previous_event.mask,
      user: current_user,
      event_type: 'breakdown_updated',
      data: { breakdown: breakdown_data },
      notes: params[:notes]
    )

    if mask_event.save
      # The after_create callback on MaskEvent will trigger mask.regenerate
      render json: {
        success: true,
        breakdown: {
          id: mask_event.id,
          mask_id: mask_event.mask_id,
          breakdown: breakdown_data,
          complete: breakdown_data.all? { |item| item.values.first.present? },
          updated_at: mask_event.updated_at,
          user: {
            id: mask_event.user.id,
            email: mask_event.user.email
          }
        }
      }
    else
      render json: {
        success: false,
        errors: mask_event.errors.full_messages
      }, status: :unprocessable_entity
    end
  end

  private

  def require_admin!
    return if current_user&.admin?

    render json: { error: 'Unauthorized. Admin access required.' }, status: :forbidden
  end
end
