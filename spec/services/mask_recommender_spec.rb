# frozen_string_literal: true

require 'rails_helper'
require 'oj'

RSpec.describe MaskRecommender, type: :service do
  let(:old_env) do
    ENV['HEROKU_ENVIRONMENT']
  end

  before do
    ENV['HEROKU_ENVIRONMENT'] = 'staging'
  end

  after do
    ENV['HEROKU_ENVIRONMENT'] = old_env
  end

  describe '.infer' do
    let(:facial) do
      {
        'bitragion_subnasale_arc' => 230,
        'face_width' => 150,
        'face_length' => 125,
        'nose_protrusion' => 28,
        'facial_hair_beard_length_mm' => 0
      }
    end

    it 'sends correct payload and maps the lambda response' do
      masks = [
        { 'id' => 111, 'name' => 'Mask A', 'style' => 'Cup' },
        { 'id' => 222, 'name' => 'Mask B', 'style' => 'Duckbill' }
      ]

      body = {
        'mask_id' => { '0' => 222 },
        'proba_fit' => { '0' => 0.9 }
      }

      allow(Mask).to receive(:with_aggregations).and_return(masks)

      allow(AwsLambdaInvokeService).to receive(:call)
        .with(
          function_name: 'mask-recommender-staging',
          payload: hash_including(
            method: 'infer',
            facial_measurements: facial,
            mask_ids: [111, 222]
          )
        ).and_return({ 'body' => Oj.dump(body) })

      result = described_class.infer(facial, mask_ids: [111, 222])

      expect(AwsLambdaInvokeService).to have_received(:call)
        .with(
          function_name: 'mask-recommender-staging',
          payload: hash_including(
            method: 'infer',
            facial_measurements: facial,
            mask_ids: [111, 222]
          )
        )

      by_id = result.index_by { |h| h['id'] }
      expect(by_id[222]['proba_fit']).to be_within(1e-6).of(0.9)
      expect(by_id[111]['proba_fit']).to be_nil
      expect(by_id[222]['name']).to eq('Mask B')
      expect(by_id[111]['name']).to eq('Mask A')
    end
  end

  describe '.train' do
    it 'sends correct payload and returns parsed body' do
      body = {
        'message' => 'Training completed successfully',
        'artifacts' => { 'model_latest' => 's3://bucket/key.pt' },
        'metrics' => { 'val_acc' => 0.8 }
      }

      allow(AwsLambdaInvokeService).to receive(:call)
        .with(
          function_name: 'mask-recommender-staging',
          payload: hash_including(
            method: 'train',
            epochs: 5,
            data_url: 'https://example.com/data.json',
            target_col: 'qlft_pass'
          )
        ).and_return({ 'body' => Oj.dump(body) })

      result = described_class.train(epochs: 5, data_url: 'https://example.com/data.json', target_col: 'qlft_pass')

      expect(AwsLambdaInvokeService).to have_received(:call)
        .with(
          function_name: 'mask-recommender-staging',
          payload: hash_including(
            method: 'train',
            epochs: 5,
            data_url: 'https://example.com/data.json',
            target_col: 'qlft_pass'
          )
        )

      expect(result['message']).to eq(body['message'])
      expect(result.dig('artifacts', 'model_latest')).to eq('s3://bucket/key.pt')
      expect(result.dig('metrics', 'val_acc')).to be_within(1e-6).of(0.8)
    end
  end
end
