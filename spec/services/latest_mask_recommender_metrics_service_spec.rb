# frozen_string_literal: true

require 'spec_helper'
require 'active_support/core_ext/object/blank'
require 'active_support/core_ext/module/delegation'
require_relative '../../app/services/latest_mask_recommender_metrics_service'

RSpec.describe LatestMaskRecommenderMetricsService do
  let(:service) { described_class.new }

  it 'exposes aggregate held-out probability metrics without individual audit rows' do
    evaluation = {
      'version' => 'held_out_probability_evaluation_v1',
      'available' => true,
      'sample_count' => 12,
      'quality' => { 'log_loss' => 0.42 },
      'at_0_5' => { 'precision' => 0.7, 'recall' => 0.6 },
      'rows' => [{ 'user_id' => 99, 'mask_id' => 5, 'probability' => 0.9 }]
    }
    allow(service).to receive(:load_metrics).and_return(
      'timestamp' => 'example', 'cross_validation' => { 'probability_evaluation' => evaluation }
    )

    result = service.call
    expect(result[:available]).to be(true)
    expect(result[:probability_evaluation]['quality']['log_loss']).to eq(0.42)
    expect(result[:probability_evaluation]).not_to have_key('rows')
  end

  it 'keeps older model artifacts available without inventing missing metrics' do
    allow(service).to receive(:load_metrics).and_return('timestamp' => 'old', 'roc_auc' => 0.75)

    expect(service.call).to include(available: true, validation_roc_auc: 0.75, probability_evaluation: nil)
  end

  it 'returns an unavailable payload for no saved metrics' do
    allow(service).to receive(:load_metrics).and_return(nil)

    expect(service.call).to include(available: false, probability_evaluation: nil)
  end
end
