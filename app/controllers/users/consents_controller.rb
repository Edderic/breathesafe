# frozen_string_literal: true

module Users
  class ConsentsController < ApplicationController
    before_action :authenticate_user!

    def create
      decision = params[:decision]
      current_version = Rails.application.config.x.consent_form_version

      case decision
      when 'accept'
        current_user.update!(
          consent_form_version_accepted: current_version,
          consent_form_accepted_at: Time.current
        )
        accepted = true
      when 'reject'
        # Intentionally do not persist rejection per current requirements
        accepted = false
      else
        render json: { error: 'invalid decision' }, status: :unprocessable_entity and return
      end

      render json: {
        accepted: accepted,
        version: current_version,
        currentUser: current_user
      }
    end
  end
end
