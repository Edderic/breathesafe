# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskRecommenderController, type: :controller do
  describe 'POST #create' do
    let(:manager) { create(:user) }
    let(:managed_user) { create(:user) }
    let(:facial_payload) do
      {
        nose_mm: 44,
        chin_mm: 46,
        top_cheek_mm: 48,
        mid_cheek_mm: 50,
        facial_hair_beard_length_mm: 0
      }
    end

    let(:inferred_masks) do
      [
        { 'id' => 1, 'proba_fit' => 0.9, 'name' => 'Mask A' },
        { 'id' => 2, 'proba_fit' => 0.7, 'name' => 'Mask B' }
      ]
    end
    let(:model_meta) { { 'timestamp' => '20260208000000' } }
    let(:context) { { 'perimeter_min' => 100, 'perimeter_max' => 200 } }

    before do
      allow(MaskRecommender).to receive(:infer_with_meta).and_return({ masks: inferred_masks, model: model_meta })
      allow(MasksDataContextualizer).to receive(:call).and_return(context)
      create(:managed_user, manager: manager, managed: managed_user)
    end

    it 'calls MaskRecommender.infer with function_base override when provided (top-level)' do
      post :create, params: {
        facial_measurements: facial_payload,
        function_base: 'mask-recommender-rf'
      }, as: :json

      expect(MaskRecommender).to have_received(:infer_with_meta).with(
        facial_payload.stringify_keys,
        function_base: 'mask-recommender-rf'
      )
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['masks']).to eq(inferred_masks)
      expect(body['context']).to eq(context)
      expect(body['model']).to eq(model_meta)
    end

    it 'calls MaskRecommender.infer with nested function_base override when provided' do
      post :create, params: {
        facial_measurements: facial_payload,
        mask_recommender: { function_base: 'mask-recommender' }
      }, as: :json

      expect(MaskRecommender).to have_received(:infer_with_meta).with(
        facial_payload.stringify_keys,
        function_base: 'mask-recommender'
      )
      expect(response).to have_http_status(:ok)
    end

    it 'permits only recommender columns and beard length' do
      noisy = facial_payload.merge(extra: 'ignore_me')
      post :create, params: { facial_measurements: noisy }, as: :json

      # Controller will stringify and permit
      expect(MaskRecommender).to have_received(:infer_with_meta) do |arg_hash, **_opts|
        expect(arg_hash).not_to have_key('extra')
      end
      expect(response).to have_http_status(:ok)
    end

    it 'returns context with recommendations' do
      post :create, params: { facial_measurements: facial_payload }, as: :json

      body = JSON.parse(response.body)
      expect(body['masks']).to eq(inferred_masks)
      expect(body['context']).to eq(context)
      expect(body['model']).to eq(model_meta)
    end

    it 'allows a manager to use recommender_user_id and merges fit test summary fields' do
      allow(controller).to receive(:current_user).and_return(manager)
      resolved_measurements = facial_payload.stringify_keys
      summary_map = {
        1 => {
          'observed_fit_pass_count' => 2,
          'observed_fit_test_count' => 3,
          'observed_fit_pass_rate' => 2.0 / 3.0,
          'observed_fit_label' => '67% (2/3)'
        }
      }

      allow(LatestRecommenderFacialMeasurementsService).to receive(:call).and_return(resolved_measurements)
      allow(MaskFitTestSummaryService).to receive(:call).and_return(summary_map)

      post :create, params: { recommender_user_id: managed_user.id }, as: :json

      expect(LatestRecommenderFacialMeasurementsService).to have_received(:call).with(
        viewer: manager,
        recommender_user_id: managed_user.id
      )
      expect(MaskRecommender).to have_received(:infer_with_meta).with(
        resolved_measurements,
        function_base: 'mask-recommender'
      )

      body = JSON.parse(response.body)
      expect(body['masks'][0]['observed_fit_label']).to eq('67% (2/3)')
      expect(body['masks'][0]['observed_fit_pass_rate']).to eq(2.0 / 3.0)
      expect(body['masks'][1]['observed_fit_label']).to be_nil
    end

    it 'returns 403 when recommender_user_id is forbidden' do
      allow(controller).to receive(:current_user).and_return(manager)
      allow(LatestRecommenderFacialMeasurementsService).to receive(:call)
        .and_raise(LatestRecommenderFacialMeasurementsService::ForbiddenError, 'forbidden')

      post :create, params: { recommender_user_id: managed_user.id }, as: :json

      expect(response).to have_http_status(:forbidden)
      expect(JSON.parse(response.body)['error']).to eq('forbidden')
    end
  end

  describe 'POST #warmup' do
    it 'calls MaskRecommender.warmup and returns ok' do
      allow(MaskRecommender).to receive(:warmup).and_return({ 'status' => 'warmed' })

      post :warmup, params: {}, as: :json

      expect(MaskRecommender).to have_received(:warmup).with(function_base: 'mask-recommender')
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['status']).to eq('ok')
      expect(body['result']).to eq({ 'status' => 'warmed' })
    end

    it 'passes function_base override for warmup' do
      allow(MaskRecommender).to receive(:warmup).and_return({ 'status' => 'warmed' })

      post :warmup, params: { function_base: 'mask-recommender-rf' }, as: :json

      expect(MaskRecommender).to have_received(:warmup).with(function_base: 'mask-recommender-rf')
      expect(response).to have_http_status(:ok)
    end
  end

  describe 'GET #status' do
    it 'returns queued when cache payload is missing' do
      allow(Rails.cache).to receive(:read).and_return(nil)

      get :status, params: { id: 'missing-job-id' }, as: :json

      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['status']).to eq('queued')
    end
  end
end
