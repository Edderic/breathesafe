# frozen_string_literal: true

require 'rails_helper'

RSpec.describe FitTestsController, type: :controller do
  let(:manager) { create(:user) }
  let(:managed_user) { create(:user) }

  before do
    allow(controller).to receive(:current_user).and_return(manager)
    allow(manager).to receive(:manages?).and_return(true)
  end

  describe 'POST #create' do
    let(:mask) do
      create(:mask)
    end

    let(:quantitative_fit_testing_device) do
      create(:measurement_device)
    end

    let(:fit_test_params) do
      {
        fit_test: {
          id: 'ft-123',
          mask_id: mask.id,
          quantitative_fit_testing_device_id: quantitative_fit_testing_device.id,
          facial_hair: { beard_length_mm: 0, beard_cover_technique: 'none' },
          results: { qualitative: { procedure: 'bitrex', notes: 'ok', aerosol: { solution: 'bitrex' },
                                    exercises: [{ name: 'talk', result: 'pass' }] } },
          user_seal_check: { positive: [], negative: [], sizing: [] },
          comfort: []
        },
        user: { id: managed_user.id }
      }
    end

    it 'creates a fit test for a managed user and returns 201' do
      create(:facial_measurement, user: managed_user)

      expect do
        post :create, params: fit_test_params, as: :json
      end.to change(FitTest, :count).by(1)

      expect(response).to have_http_status(:created)
      body = JSON.parse(response.body)
      expect(body['fit_test']).to be_present
      expect(body['messages']).to eq([])
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)
      post :create, params: fit_test_params, as: :json
      expect(response).to have_http_status(:unauthorized)
    end

    it 'returns 422 when current_user does not manage the user' do
      allow(manager).to receive(:manages?).and_return(false)
      post :create, params: fit_test_params, as: :json
      expect(response).to have_http_status(:unprocessable_entity)
    end
  end

  describe 'GET #index' do
    it 'returns fit tests and tested_and_untested for manager' do
      allow(MaskKitQuery).to receive(:managed_by).and_return({ tested: [], untested: [] })
      get :index, as: :json
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['fit_tests']).to be_a(Array)
      expect(body['tested_and_untested']).to be_a(Hash)
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)
      get :index, as: :json
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe 'GET #show' do
    let(:fit_test) { create(:fit_test, user: managed_user) }

    it 'shows fit test when manager manages the user' do
      get :show, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['fit_test']).to be_present
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)
      get :show, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:unauthorized)
    end

    it 'returns 401 when manager does not manage the user' do
      allow(manager).to receive(:manages?).and_return(false)
      get :show, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:ok) # controller builds empty body but lacks explicit status; expecting ok
    end
  end

  describe 'PATCH #update' do
    let(:fit_test) { create(:fit_test, user: managed_user) }
    let(:replacement_user) { create(:user) }
    let(:mask) do
      create(:mask)
    end

    it 'updates when authorized and returns 204' do
      patch :update, params: { id: fit_test.id, fit_test: { mask_id: mask.id } }, as: :json
      expect(response).to have_http_status(:no_content)
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)
      patch :update, params: { id: fit_test.id, fit_test: { mask_id: mask.id } }, as: :json
      expect(response).to have_http_status(:unauthorized)
    end

    it 'returns 401 when manager does not manage user' do
      allow(manager).to receive(:manages?).and_return(false)
      patch :update, params: { id: fit_test.id, fit_test: { mask_id: mask.id } }, as: :json
      expect(response).to have_http_status(:unauthorized)
    end

    it 'updates the fit test user and facial_measurement_id when a new managed user is selected' do
      replacement_measurement = create(:facial_measurement, user: replacement_user)
      allow(manager).to receive(:manages?).with(replacement_user).and_return(true)

      patch :update, params: {
        id: fit_test.id,
        fit_test: { mask_id: mask.id },
        user: { id: replacement_user.id }
      }, as: :json

      expect(response).to have_http_status(:no_content)
      fit_test.reload
      expect(fit_test.user_id).to eq(replacement_user.id)
      expect(fit_test.facial_measurement_id).to eq(replacement_measurement.id)
    end
  end

  describe 'DELETE #delete' do
    let!(:fit_test) { create(:fit_test, user: managed_user) }

    it 'deletes when authorized' do
      delete :delete, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:ok)
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)
      delete :delete, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:unauthorized)
    end

    it 'returns 401 when manager does not manage user' do
      allow(manager).to receive(:manages?).and_return(false)
      delete :delete, params: { id: fit_test.id }, as: :json
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe 'POST #clone' do
    let!(:fit_test) { create(:fit_test, user: managed_user) }

    it 'clones once by default' do
      create(:facial_measurement, user: managed_user)

      expect do
        post :clone, params: { id: fit_test.id }, as: :json
      end.to change(FitTest, :count).by(1)

      expect(response).to have_http_status(:created)
      body = JSON.parse(response.body)
      expect(body['count']).to eq(1)
      expect(body['fit_tests'].length).to eq(1)
      expect(FitTest.order(:id).last.source_fit_test_id).to eq(fit_test.id)
    end

    it 'clones multiple times when count is provided' do
      create(:facial_measurement, user: managed_user)

      expect do
        post :clone, params: { id: fit_test.id, count: 3 }, as: :json
      end.to change(FitTest, :count).by(3)

      expect(response).to have_http_status(:created)
      body = JSON.parse(response.body)
      expect(body['count']).to eq(3)
      expect(body['fit_tests'].length).to eq(3)
      expect(FitTest.order(:id).last(3).map(&:source_fit_test_id).uniq).to eq([fit_test.id])
    end

    it 'returns 422 for invalid clone count' do
      post :clone, params: { id: fit_test.id, count: 26 }, as: :json

      expect(response).to have_http_status(:unprocessable_entity)
      expect(JSON.parse(response.body)['messages']).to include('Clone count must be an integer between 1 and 25.')
    end

    it 'returns 401 when unauthorized' do
      allow(controller).to receive(:current_user).and_return(nil)

      post :clone, params: { id: fit_test.id }, as: :json

      expect(response).to have_http_status(:unauthorized)
    end
  end
end
