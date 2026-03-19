# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Admin::UsersController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:admin) { create(:user, :admin) }
  let(:non_admin) { create(:user) }

  describe 'GET #index' do
    context 'when admin' do
      before { sign_in admin }

      it 'returns users with profile fields' do
        user = create(:user, email: 'person@example.com')
        profile = user.profile || create(:profile, user: user)
        profile.update!(first_name: 'Pat', last_name: 'Smith')

        get :index, params: { search: 'person@example.com' }, format: :json

        expect(response).to have_http_status(:ok)
        body = JSON.parse(response.body)
        expect(body['users'].length).to eq(1)
        expect(body['users'][0]['id']).to eq(user.id)
        expect(body['users'][0]['email']).to eq('person@example.com')
        expect(body['users'][0]['first_name']).to eq('Pat')
        expect(body['users'][0]['last_name']).to eq('Smith')
      end

      it 'supports ids lookup' do
        user = create(:user)
        profile = user.profile || create(:profile, user: user)
        profile.update!(first_name: 'ID', last_name: 'Lookup')

        get :index, params: { ids: user.id }, format: :json

        expect(response).to have_http_status(:ok)
        body = JSON.parse(response.body)
        expect(body['users'].map { |u| u['id'] }).to include(user.id)
      end
    end

    context 'when non-admin' do
      before { sign_in non_admin }

      it 'returns forbidden' do
        get :index, format: :json
        expect(response).to have_http_status(:forbidden)
      end
    end
  end
end
