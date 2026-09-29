# frozen_string_literal: true

module Admin
  class MaskProposalsController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def index
      scope = MaskProposal.includes(:mask).order(:id)
      scope = scope.where(id: params[:id]) if params[:id].present?
      scope = scope.where(resolved_at: nil) unless params[:include_resolved] == 'true'
      rows = scope.where('mask_proposals.id > ?', params[:after_id].to_i).limit(51).to_a
      counts = MaskProposalLink.where(mask_proposal_id: rows.first(50).map(&:id)).group(:mask_proposal_id).count
      response.headers['Cache-Control'] = 'no-store'
      render json: { proposals: rows.first(50).map do |row|
        serialize(row, counts.fetch(row.id, 0))
      end, has_more: rows.size > 50 }
    end

    def update
      proposal = MaskProposal.find(params[:id])
      name = params[:name]
      if params[:mask_id].blank? && (!name.is_a?(String) || name.strip.empty? || name.length > 200 ||
                                   name.match?(/[[:cntrl:]]/))
        return render json: { error: 'Enter a mask model name (up to 200 characters).' }, status: :unprocessable_entity
      end

      MaskProposalResolution.call(proposal: proposal, reviewer: current_user, mask_id: params[:mask_id],
                                  name: name&.strip)
      render json: serialize(proposal)
    rescue MaskProposalResolution::AlreadyResolved => e
      render json: { error: e.message }, status: :conflict
    rescue ActiveRecord::RecordInvalid => e
      render json: { error: e.record.errors.full_messages.join(', ') }, status: :unprocessable_entity
    rescue ActiveRecord::RecordNotFound
      render json: { error: 'Proposal or canonical mask not found.' }, status: :not_found
    end

    private

    def serialize(row, test_count = row.mask_proposal_links.count)
      { id: row.id, name: row.name, mask_id: row.mask_id, mask_name: row.mask&.unique_internal_model_code,
        resolved_at: row.resolved_at, created_at: row.created_at, test_count: test_count }
    end

    def ensure_admin
      render json: { error: 'Unauthorized' }, status: :forbidden unless current_user&.admin?
    end
  end
end
