# frozen_string_literal: true

module Admin
  class AnonymousContributionsController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin
    before_action :prevent_caching

    rescue_from AnonymousContributionDeletion::Error do |error|
      render json: { error: error.message, dependent_ids: error.dependent_ids }, status: :conflict
    end
    rescue_from ActiveRecord::InvalidForeignKey, ActiveRecord::Deadlocked, ActiveRecord::RecordNotDestroyed do
      render json: { error: 'The submissions could not be deleted. Refresh and review your selection again.' },
             status: :conflict
    end

    def index
      scope = AnonymousContribution.order(id: :desc)
      if params[:receipt].present?
        receipt = params[:receipt].to_s
        unless receipt.match?(/\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\z/i)
          return render json: { error: 'Enter a complete receipt ID.' }, status: :unprocessable_entity
        end

        scope = scope.where(contribution_id: receipt)
      end
      if params[:participant].present?
        unless params[:participant].to_s.match?(/\A[1-9][0-9]{0,17}\z/)
          return render json: { error: 'Enter a numeric participant ID.' }, status: :unprocessable_entity
        end

        scope = scope.where(anonymous_participant_id: params[:participant])
      end
      if params[:before_id].present?
        unless params[:before_id].to_s.match?(/\A[1-9][0-9]{0,17}\z/)
          return render json: { error: 'Invalid page cursor. Refresh the list.' }, status: :unprocessable_entity
        end

        scope = scope.where('id < ?', params[:before_id].to_i)
      end
      rows = scope.limit(26).to_a
      render json: { contributions: rows.first(25).map { |row| AnonymousContributionDeletion.serialize(row) },
                     has_more: rows.size > 25 }
    end

    def deletion_preview
      render json: AnonymousContributionDeletion.new(current_user).preview(params[:contribution_ids])
    end

    def destroy_selected
      ids = AnonymousContributionDeletion.new(current_user).delete(params[:token])
      render json: { deleted_ids: ids }
    end

    private

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Sign in as an admin to manage anonymous submissions.' }, status: :forbidden
    end

    def prevent_caching
      response.headers['Cache-Control'] = 'no-store'
    end
  end
end
