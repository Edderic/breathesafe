class ApplicationController < ActionController::Base
  respond_to :html, :json

  def unauthorized?
    !current_user
  end
end
