# frozen_string_literal: true

module Users
  class ConsentsController < ApplicationController
    before_action :authenticate_user!

    def create
      decision = params[:decision]
      forms_to_accept = params[:forms] || ['consent_form'] # Default to consent_form for backward compatibility

      case decision
      when 'accept'
        # Get current versions for all forms
        current_versions = {
          'consent_form' => Rails.application.config.consent_form_version,
          'disclaimer' => Rails.application.config.disclaimer_version,
          'terms_of_service' => Rails.application.config.terms_of_service_version,
          'privacy_policy' => Rails.application.config.privacy_policy_version
        }

        # Accept all specified forms
        forms_to_accept.each do |form_name|
          version = current_versions[form_name]
          if version.present?
            current_user.accept_form(form_name, version)
          else
            Rails.logger.warn("Unknown form type: #{form_name}")
          end
        end

        # Also update legacy fields for consent_form for backward compatibility
        if forms_to_accept.include?('consent_form')
          current_user.consent_form_version_accepted = current_versions['consent_form']
          current_user.consent_form_accepted_at = Time.current
        end

        current_user.save!
        current_user.reload

        accepted = true
      when 'reject'
        # Intentionally do not persist rejection per current requirements
        accepted = false
      else
        render json: { error: 'invalid decision' }, status: :unprocessable_entity and return
      end

      render json: {
        accepted: accepted,
        forms: current_user.forms,
        currentUser: current_user.reload
      }
    end
  end
end
