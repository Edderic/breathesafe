# frozen_string_literal: true

# Let user get csrf_token
class CsrfTokensController < ApplicationController
  def show
    render json: { csrf_token: form_authenticity_token }
  end
end
