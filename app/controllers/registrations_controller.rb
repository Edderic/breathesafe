class RegistrationsController < Devise::RegistrationsController
  skip_before_action :require_no_authentication

  clear_respond_to
  respond_to :json

  def is_signed_in
    respond_to do |format|
      puts(current_user)

      format.json do
        render json: {
          updateSignedIn: !!current_user
        }.to_json
      end
    end
  end

  private

  def sign_up(_resource_name, _resource)
    true
  end
end
