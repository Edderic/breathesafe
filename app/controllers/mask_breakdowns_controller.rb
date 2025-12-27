# frozen_string_literal: true

class MaskBreakdownsController < ApplicationController
  before_action :authenticate_user!
  before_action :require_admin!

  # GET /mask_breakdowns.json
  # Returns all masks with their latest breakdown (if any)
  def index
    masks = Mask.order(:unique_internal_model_code)
                .select(:id, :unique_internal_model_code)
                .to_a

    # Get latest breakdown for each mask
    mask_data = masks.map do |mask|
      latest_breakdown = MaskBreakdown.latest_for_mask(mask.id).first
      tokens = MaskBreakdown.tokenize(mask.unique_internal_model_code)

      {
        id: mask.id,
        unique_internal_model_code: mask.unique_internal_model_code,
        tokens: tokens,
        breakdown: latest_breakdown&.breakdown || [],
        breakdown_id: latest_breakdown&.id,
        breakdown_complete: latest_breakdown&.complete? || false,
        breakdown_updated_at: latest_breakdown&.updated_at,
        breakdown_user: if latest_breakdown&.user
                          {
                            id: latest_breakdown.user.id,
                            email: latest_breakdown.user.email
                          }
                        end
      }
    end

    render json: {
      masks: mask_data,
      total_count: masks.length,
      completed_count: mask_data.count { |m| m[:breakdown_complete] },
      categories: MaskBreakdown::VALID_CATEGORIES
    }
  end

  # GET /mask_breakdowns/:id.json
  # Returns a specific mask with its breakdown
  def show
    mask = Mask.find(params[:id])
    latest_breakdown = MaskBreakdown.latest_for_mask(mask.id).first
    tokens = MaskBreakdown.tokenize(mask.unique_internal_model_code)

    render json: {
      id: mask.id,
      unique_internal_model_code: mask.unique_internal_model_code,
      tokens: tokens,
      breakdown: latest_breakdown&.breakdown || [],
      breakdown_id: latest_breakdown&.id,
      breakdown_complete: latest_breakdown&.complete? || false,
      breakdown_updated_at: latest_breakdown&.updated_at,
      breakdown_user: if latest_breakdown&.user
                        {
                          id: latest_breakdown.user.id,
                          email: latest_breakdown.user.email
                        }
                      end,
      categories: MaskBreakdown::VALID_CATEGORIES
    }
  end

  # POST /mask_breakdowns.json
  # Creates or updates a breakdown for a mask
  def create
    mask = Mask.find(params[:mask_id])
    breakdown_data = params[:breakdown] || []

    # Create new breakdown record
    mask_breakdown = MaskBreakdown.new(
      mask: mask,
      user: current_user,
      breakdown: breakdown_data,
      notes: params[:notes]
    )

    if mask_breakdown.save
      render json: {
        success: true,
        breakdown: {
          id: mask_breakdown.id,
          mask_id: mask_breakdown.mask_id,
          breakdown: mask_breakdown.breakdown,
          complete: mask_breakdown.complete?,
          updated_at: mask_breakdown.updated_at,
          user: {
            id: mask_breakdown.user.id,
            email: mask_breakdown.user.email
          }
        }
      }, status: :created
    else
      render json: {
        success: false,
        errors: mask_breakdown.errors.full_messages
      }, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /mask_breakdowns/:id.json
  # Updates an existing breakdown
  def update
    mask_breakdown = MaskBreakdown.find(params[:id])
    breakdown_data = params[:breakdown] || []

    # Create a new record instead of updating (for audit trail)
    new_breakdown = MaskBreakdown.new(
      mask: mask_breakdown.mask,
      user: current_user,
      breakdown: breakdown_data,
      notes: params[:notes]
    )

    if new_breakdown.save
      render json: {
        success: true,
        breakdown: {
          id: new_breakdown.id,
          mask_id: new_breakdown.mask_id,
          breakdown: new_breakdown.breakdown,
          complete: new_breakdown.complete?,
          updated_at: new_breakdown.updated_at,
          user: {
            id: new_breakdown.user.id,
            email: new_breakdown.user.email
          }
        }
      }
    else
      render json: {
        success: false,
        errors: new_breakdown.errors.full_messages
      }, status: :unprocessable_entity
    end
  end

  private

  def require_admin!
    return if current_user&.admin?

    render json: { error: 'Unauthorized. Admin access required.' }, status: :forbidden
  end
end
