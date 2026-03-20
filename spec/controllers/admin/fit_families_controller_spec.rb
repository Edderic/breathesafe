# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Admin::FitFamiliesController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:admin) { create(:user, :admin) }
  let(:non_admin) { create(:user) }

  describe 'GET #index' do
    before do
      create(:fit_family, name: 'Trident Family')
      sign_in admin
    end

    it 'returns fit families for admins' do
      get :index, format: :json

      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['fit_families'].first['name']).to eq('Trident Family')
    end
  end

  describe 'POST #create' do
    before { sign_in admin }

    it 'creates a fit family' do
      expect do
        post :create, params: { fit_family: { name: 'Laianzhi KN100 Family' } }, format: :json
      end.to change(FitFamily, :count).by(1)

      expect(response).to have_http_status(:created)
      expect(JSON.parse(response.body).dig('fit_family', 'name')).to eq('Laianzhi KN100 Family')
    end

    it 'returns forbidden for non-admins' do
      sign_out admin
      sign_in non_admin

      post :create, params: { fit_family: { name: 'Hidden Family' } }, format: :json

      expect(response).to have_http_status(:forbidden)
    end
  end
end
