# frozen_string_literal: true

# Overrides Devise::RegistrationController
# Adds an is_signed_in method that is used in the frontend
class RegistrationsController < Devise::RegistrationsController
  skip_before_action :verify_authenticity_token
  clear_respond_to
  respond_to :json

  def is_signed_in
    respond_to do |format|
      Rails.logger.debug(current_user)

      format.json do
        render json: {
          updateSignedIn: !current_user.nil?
        }.to_json
      end
    end
  end

  private

  def sign_up(_resource_name, _resource)
    true
  end
end
