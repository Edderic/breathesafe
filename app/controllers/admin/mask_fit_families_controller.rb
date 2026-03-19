# frozen_string_literal: true

module Admin
  class MaskFitFamiliesController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def update
      mask = Mask.find(params[:mask_id])
      fit_family = FitFamily.find(mask_fit_family_params[:fit_family_id])

      mask.update!(fit_family: fit_family)

      render json: {
        success: true,
        mask: {
          id: mask.id,
          fit_family_id: mask.fit_family_id
        }
      }, status: :ok
    rescue ActiveRecord::RecordInvalid => e
      render json: { error: e.record.errors.full_messages.to_sentence }, status: :unprocessable_entity
    rescue ActiveRecord::RecordNotFound
      render json: { error: 'Not found' }, status: :not_found
    end

    private

    def mask_fit_family_params
      params.require(:mask_fit_family).permit(:fit_family_id)
    end

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Unauthorized' }, status: :forbidden
    end
  end
end
