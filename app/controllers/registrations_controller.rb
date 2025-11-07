# frozen_string_literal: true

# Overrides Devise::RegistrationController
# Adds an is_signed_in method that is used in the frontend
class RegistrationsController < Devise::RegistrationsController
  skip_before_action :verify_authenticity_token
  clear_respond_to
  respond_to :json

  def signed_in?
    respond_to do |format|
      Rails.logger.debug(current_user)

      format.json do
        render json: {
          updateSignedIn: !current_user.nil?
        }.to_json
      end
    end
  end

  def create
    # Extract accept_consent before building resource since it's not a User attribute
    accept_consent = params[:user]&.delete(:accept_consent) || params.dig(:registration, :user)&.delete(:accept_consent)

    build_resource(sign_up_params)

    resource.save
    yield resource if block_given?
    if resource.persisted?
      # If user accepted consent during registration, set consent fields
      if [true, 'true', '1', true].include?(accept_consent)
        current_version = Rails.application.config.x.consent_form_version
        if current_version.is_a?(String) && current_version.present?
          # Use update to respect validations
          resource.update(
            consent_form_version_accepted: current_version,
            consent_form_accepted_at: Time.current
          )
        end
      end

      if resource.active_for_authentication?
        set_flash_message! :notice, :signed_up
        sign_up(resource_name, resource)
        respond_with resource, location: after_sign_up_path_for(resource)
      else
        set_flash_message! :notice, :"signed_up_but_#{resource.inactive_message}"
        expire_data_after_sign_in!
        respond_with resource, location: after_inactive_sign_up_path_for(resource)
      end
    else
      clean_up_passwords resource
      set_minimum_password_length
      respond_with resource
    end
  end

  private

  def sign_up_params
    params.require(:user).permit(:email, :password, :password_confirmation)
  end

  def sign_up(_resource_name, _resource)
    true
  end
end
