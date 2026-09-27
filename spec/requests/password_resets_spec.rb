# frozen_string_literal: true

require 'rails_helper'

RSpec.describe 'Password resets', type: :request do
  before do
    ActionMailer::Base.deliveries.clear
  end

  it 'renders the forgot password page' do
    get '/users/password/new'

    expect(response).to have_http_status(:ok)
    expect(response.body).to include('Forgot your password?')
  end

  it 'sends reset password instructions for a confirmed user' do
    user = create(:user, email: 'reset@example.com')

    expect do
      post '/users/password', params: { user: { email: user.email } }
    end.to change { ActionMailer::Base.deliveries.count }.by(1)

    expect(response).to redirect_to('/#/signin')
    expect(response).to have_http_status(:found)
    expect(ActionMailer::Base.deliveries.last.to).to include(user.email)
  end

  it 'updates the password when given a valid reset token' do
    user = create(:user, password: 'old-password', password_confirmation: 'old-password')
    raw_token = user.send_reset_password_instructions

    put '/users/password', params: {
      user: {
        reset_password_token: raw_token,
        password: 'new-password-123',
        password_confirmation: 'new-password-123'
      }
    }

    expect(response).to redirect_to('/#/respirator_users')
    expect(response).to have_http_status(:found)
    expect(user.reload.valid_password?('new-password-123')).to be(true)
  end
end
