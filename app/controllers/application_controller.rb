# frozen_string_literal: true

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
end
