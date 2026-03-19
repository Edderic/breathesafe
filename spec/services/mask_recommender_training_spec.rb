# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskRecommenderTraining do
  describe '.call' do
    it 'does not enable class_reweight by default for custom_lr' do
      allow(AwsLambdaInvokeService).to receive(:call).and_return({ 'status' => 'started' })
      allow(ENV).to receive(:fetch).with('HEROKU_ENVIRONMENT', '').and_return('development')

      described_class.call(payload: { model_type: 'custom_lr' })

      expect(AwsLambdaInvokeService).to have_received(:call).with(
        function_name: 'mask-recommender-development',
        region: AwsLambdaInvokeService::DEFAULT_REGION,
        payload: hash_including(
          model_type: 'custom_lr',
          epochs: 200,
          learning_rate: 0.01,
          retrain_with_full: true,
          class_reweight: false,
          method: 'train'
        )
      )
    end
  end
end
