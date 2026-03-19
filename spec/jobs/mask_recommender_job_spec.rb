# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskRecommenderJob, type: :job do
  describe '#perform' do
    it 'stores context alongside masks in the cached async result' do
      job_id = 'test-job-id'
      cache_key = described_class.cache_key(job_id)
      allow(Rails.cache).to receive(:write)

      allow(MaskRecommender).to receive(:infer_with_meta).and_return(
        {
          masks: [{ 'id' => 123, 'unique_internal_model_code' => 'Example Mask' }],
          model: { 'timestamp' => '20260315' }
        }
      )
      allow(MasksDataContextualizer).to receive(:call).and_return(
        { initial_cost_max: 12.5 }
      )

      described_class.perform_now(
        job_id: job_id,
        facial_measurements: { 'nose_mm' => 45 },
        function_base: 'mask-recommender',
        model_type: 'custom_lr'
      )

      expect(Rails.cache).to have_received(:write).with(
        cache_key,
        hash_including(
          status: 'complete',
          result: {
            masks: [{ 'id' => 123, 'unique_internal_model_code' => 'Example Mask' }],
            context: { initial_cost_max: 12.5 }
          },
          model: { 'timestamp' => '20260315' }
        ),
        expires_in: described_class::CACHE_TTL
      )
    end
  end
end
