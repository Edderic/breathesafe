# frozen_string_literal: true

module Admin
  class MaskDuplicatesController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def create
      target_mask_id = params[:target_mask_id] || params.dig(:duplicate_link, :target_mask_id)
      if target_mask_id.blank?
        return render json: { error: 'target_mask_id is required' }, status: :unprocessable_entity
      end

      result = MaskDuplicateLinkService.call(
        child_mask_id: params[:mask_id],
        target_mask_id: target_mask_id,
        user: current_user,
        notes: params[:notes]
      )

      render json: {
        success: true,
        duplicate_link: result
      }, status: :ok
    rescue MaskDuplicateLinkService::Error => e
      render json: { error: e.message }, status: :unprocessable_entity
    end

    def destroy
      result = MaskDuplicateUnlinkService.call(
        mask_id: params[:mask_id],
        user: current_user,
        notes: params[:notes]
      )

      render json: {
        success: true,
        duplicate_link: result
      }, status: :ok
    rescue MaskDuplicateUnlinkService::Error => e
      render json: { error: e.message }, status: :unprocessable_entity
    end

    private

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Unauthorized' }, status: :forbidden
    end
  end
end
