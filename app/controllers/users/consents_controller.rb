# frozen_string_literal: true

module Users
  class ConsentsController < ApplicationController
    before_action :authenticate_user!

    def create
      decision = params[:decision]
      current_version = Rails.application.config.x.consent_form_version

      # Ensure current_version is a string and not nil
      unless current_version.is_a?(String) && current_version.present?
        Rails.logger.error("Invalid consent_form_version: #{current_version.inspect}")
        render json: { error: 'consent form version not configured' }, status: :internal_server_error and return
      end

      case decision
      when 'accept'
        # Explicitly ensure we're setting a string value
        version_string = current_version.to_s
        current_user.update!(
          consent_form_version_accepted: version_string,
          consent_form_accepted_at: Time.current
        )

        # Reload to ensure we have the latest data
        current_user.reload

        # Verify the value was set correctly
        if current_user.consent_form_version_accepted != version_string
          # rubocop:disable Layout/LineLength
          Rails.logger.error("Failed to set consent_form_version_accepted. Expected: #{version_string.inspect}, Got: #{current_user.consent_form_version_accepted.inspect}")
          # rubocop:enable Layout/LineLength
        end

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
        currentUser: current_user.reload
      }
    end
  end
end
