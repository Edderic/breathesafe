# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskRecommenderController, type: :controller do
  describe 'POST #create' do
    let(:facial_payload) do
      {
        face_width: 140,
        face_length: 120,
        nose_protrusion: 25,
        bitragion_subnasale_arc: 230,
        facial_hair_beard_length_mm: 0
      }
    end

    before do
      allow(MaskRecommender).to receive(:infer).and_return([
                                                             { 'id' => 1, 'proba_fit' => 0.9, 'name' => 'Mask A' },
                                                             { 'id' => 2, 'proba_fit' => 0.7, 'name' => 'Mask B' }
                                                           ])
    end

    it 'calls MaskRecommender.infer with function_base override when provided (top-level)' do
      post :create, params: {
        facial_measurements: facial_payload,
        function_base: 'mask-recommender-rf'
      }, as: :json

      expect(MaskRecommender).to have_received(:infer).with(facial_payload.stringify_keys,
                                                            function_base: 'mask-recommender-rf')
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body).to be_an(Array)
      expect(body.length).to eq(2)
    end

    it 'calls MaskRecommender.infer with nested function_base override when provided' do
      post :create, params: {
        facial_measurements: facial_payload,
        mask_recommender: { function_base: 'mask-recommender' }
      }, as: :json

      expect(MaskRecommender).to have_received(:infer).with(facial_payload.stringify_keys,
                                                            function_base: 'mask-recommender')
      expect(response).to have_http_status(:ok)
    end

    it 'permits only recommender columns and beard length' do
      noisy = facial_payload.merge(extra: 'ignore_me')
      post :create, params: { facial_measurements: noisy }, as: :json

      # Controller will stringify and permit
      expect(MaskRecommender).to have_received(:infer) do |arg_hash, **_opts|
        expect(arg_hash).not_to have_key('extra')
      end
      expect(response).to have_http_status(:ok)
    end
  end
end
