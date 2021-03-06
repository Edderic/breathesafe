class ApplicationController < ActionController::Base
  skip_before_action :verify_authenticity_token, :only => [:create]
  respond_to :html, :json

  def unauthorized?
    !current_user
  end
end
