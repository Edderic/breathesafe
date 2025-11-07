# frozen_string_literal: true

# Controller that acts as a superclass for many others
class ApplicationController < ActionController::Base
  include ActionController::Cookies
  include ActionController::RequestForgeryProtection

  respond_to :html, :json
  before_action :set_csrf_cookie

  protect_from_forgery with: :exception

  def set_csrf_cookie
    cookies['CSRF-TOKEN'] = form_authenticity_token
  end

  def unauthorized?
    !current_user
  end

  # Helper method to safely get consent form version
  # Handles cases where config.x.consent_form_version might return OrderedOptions
  def consent_form_version
    config_value = Rails.application.config.x.consent_form_version

    # If it's already a string, return it
    return config_value if config_value.is_a?(String)

    # If it's an OrderedOptions object (empty or not), try to access the value directly
    if config_value.is_a?(ActiveSupport::OrderedOptions)
      # Try accessing via the config.x object directly
      direct_value = Rails.application.config.x[:consent_form_version]
      return direct_value if direct_value.is_a?(String) && direct_value.present?

      # Fallback to default
      return '2025-10-25'
    end

    # Try to convert to string if possible
    if config_value.respond_to?(:to_s) && !config_value.to_s.empty? && config_value.to_s != config_value.class.to_s
      return config_value.to_s
    end

    # Final fallback
    '2025-10-25'
  end
end
