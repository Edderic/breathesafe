# frozen_string_literal: true

class MaskBreakdownsController < ApplicationController
  include MaskTokenizer

  before_action :authenticate_user!
  before_action :require_admin!

  # GET /mask_breakdowns.json
  # Returns paginated masks with latest breakdown data
  def index
    page = [params.fetch(:page, 1).to_i, 1].max
    per_page = params.fetch(:per_page, 100).to_i
    per_page = 100 if per_page <= 0
    per_page = [per_page, 100].min
    filter = params[:filter].to_s
    filter = 'all' unless %w[all complete incomplete].include?(filter)

    masks = Mask.order(:unique_internal_model_code)
                .select(:id, :unique_internal_model_code, :current_state)
                .to_a

    latest_events_by_mask_id = latest_breakdown_events_by_mask_id(masks.map(&:id))

    all_rows = masks.map do |mask|
      latest_event = latest_events_by_mask_id[mask.id]
      breakdown = breakdown_for(mask, latest_event)
      requires_review = breakdown_requires_review?(latest_event)
      breakdown_complete = breakdown_complete?(breakdown, requires_review)

      {
        id: mask.id,
        unique_internal_model_code: mask.unique_internal_model_code,
        tokens: MaskTokenizer.tokenize(mask.unique_internal_model_code),
        breakdown: breakdown,
        breakdown_columns: build_breakdown_columns(breakdown),
        breakdown_id: latest_event&.id,
        breakdown_complete: breakdown_complete,
        breakdown_requires_review: requires_review,
        breakdown_updated_at: latest_event&.updated_at,
        breakdown_user: if latest_event&.user
                          {
                            id: latest_event.user.id,
                            email: latest_event.user.email
                          }
                        end
      }
    end

    filtered_rows =
      case filter
      when 'complete'
        all_rows.select { |row| row[:breakdown_complete] }
      when 'incomplete'
        all_rows.reject { |row| row[:breakdown_complete] }
      else
        all_rows
      end

    total_count = filtered_rows.length
    total_pages = (total_count.to_f / per_page).ceil
    page = [page, total_pages].min if total_pages.positive?
    offset = (page - 1) * per_page
    paged_rows = filtered_rows.slice(offset, per_page) || []

    render json: {
      masks: paged_rows,
      total_count: all_rows.length,
      completed_count: all_rows.count { |row| row[:breakdown_complete] },
      filtered_count: total_count,
      categories: MaskTokenizer::VALID_CATEGORIES,
      pagination: {
        page: page,
        per_page: per_page,
        total_pages: total_pages,
        total_count: total_count
      }
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
    breakdown = breakdown_for(mask, latest_event)
    requires_review = breakdown_requires_review?(latest_event)

    render json: {
      id: mask.id,
      unique_internal_model_code: mask.unique_internal_model_code,
      tokens: tokens,
      breakdown: breakdown,
      breakdown_columns: build_breakdown_columns(breakdown),
      breakdown_id: latest_event&.id,
      breakdown_complete: breakdown_complete?(breakdown, requires_review),
      breakdown_requires_review: requires_review,
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
      data: {
        breakdown: breakdown_data,
        requires_review: false,
        source: 'manual'
      },
      notes: params[:notes]
    )

    if mask_event.save
      complete = breakdown_complete?(breakdown_data, false)
      # The after_create callback on MaskEvent will trigger mask.regenerate
      render json: {
        success: true,
        breakdown: {
          id: mask_event.id,
          mask_id: mask_event.mask_id,
          breakdown: breakdown_data,
          complete: complete,
          requires_review: false,
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
      data: {
        breakdown: breakdown_data,
        requires_review: false,
        source: 'manual'
      },
      notes: params[:notes]
    )

    if mask_event.save
      complete = breakdown_complete?(breakdown_data, false)
      # The after_create callback on MaskEvent will trigger mask.regenerate
      render json: {
        success: true,
        breakdown: {
          id: mask_event.id,
          mask_id: mask_event.mask_id,
          breakdown: breakdown_data,
          complete: complete,
          requires_review: false,
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

  def latest_breakdown_events_by_mask_id(mask_ids)
    return {} if mask_ids.blank?

    MaskEvent.where(mask_id: mask_ids, event_type: 'breakdown_updated')
             .select('DISTINCT ON (mask_id) mask_events.*')
             .includes(:user)
             .order(Arel.sql('mask_id, created_at DESC'))
             .index_by(&:mask_id)
  end

  def breakdown_for(mask, latest_event)
    event_breakdown = latest_event&.data&.dig('breakdown')
    return event_breakdown if event_breakdown.is_a?(Array)

    current_state = mask.current_state || {}
    cached_breakdown = current_state.dig('current_state', 'breakdown') || current_state['breakdown']
    cached_breakdown.is_a?(Array) ? cached_breakdown : []
  end

  def breakdown_requires_review?(latest_event)
    latest_event&.data&.dig('requires_review') == true
  end

  def breakdown_complete?(breakdown, requires_review)
    return false if requires_review

    breakdown.present? && breakdown.all? { |item| item.values.first.present? }
  end

  def build_breakdown_columns(breakdown)
    columns = MaskTokenizer::VALID_CATEGORIES.index_with { [] }

    Array(breakdown).each do |entry|
      next unless entry.is_a?(Hash)

      token, category = entry.first
      category = category.to_s
      next if token.blank? || !columns.key?(category)

      columns[category] << token
    end

    columns.transform_values { |tokens| tokens.compact.map(&:to_s).map(&:strip).reject(&:blank?).uniq }
  end
end
