# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskMatching::AnonymousSuggestions do
  include ActiveJob::TestHelper
  include ActiveSupport::Testing::TimeHelpers

  let(:cache) { ActiveSupport::Cache::MemoryStore.new }
  let(:admin) do
    User.create!(email: 'ner-matching@example.test', password: 'test-password-123', confirmed_at: Time.current)
  end
  let(:query) { 'Zimi B95-XL-01 White' }
  # Output verified against the repository's actual trained CRF model.
  let(:prediction) do
    { breakdown: [{ 'Zimi' => 'brand' }, { 'B95' => 'model' }, { 'XL' => 'model' },
                  { '01' => 'model' }, { 'White' => 'color' }] }
  end
  let(:xl_breakdown) { [{ 'Zimi' => 'brand' }, { 'B95' => 'model' }, { 'XL' => 'model' }] }

  before do
    allow(Rails).to receive(:cache).and_return(cache)
    ActiveJob::Base.queue_adapter = :test
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(prediction)
  end

  after { clear_enqueued_jobs }

  def catalog(name, breakdown = nil, **attributes)
    mask = Mask.create!({ author: admin, unique_internal_model_code: name }.merge(attributes))
    mask.update!(current_state: breakdown.nil? ? {} : { 'breakdown' => breakdown })
    mask
  end

  it 'ranks the actual Zimi example first while rejecting size conflicts and duplicates' do
    xl = catalog('Zimi B95-XL', xl_breakdown)
    catalog('Zimi B95-S', [{ 'Zimi' => 'brand' }, { 'B95' => 'model' }, { 'S' => 'size' }])
    catalog('Zimi duplicate', xl_breakdown, duplicate_of: xl.id)
    results = described_class.call(query)
    expect(results.pluck(:id)).to eq([xl.id])
    expect(results.first[:score]).to be > 0.8
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).with(query, seconds: 5).once
    expect(enqueued_jobs).to be_empty
  end

  it 'ignores color tokens while retaining numeric model suffixes' do
    catalog('Zimi B95-XL', xl_breakdown)
    white = described_class.call(query)
    black = prediction.deep_dup
    black[:breakdown][-1] = { 'Black' => 'color' }
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(black)
    expect(described_class.call('Zimi B95-XL-01 Black')).to eq(white)
    expect(MaskMatching::PredictionCache.read(query)[:model]).to include('01')
  end

  it 'matches misspelled brands using component similarity' do
    xl = catalog('Zimi B95-XL', xl_breakdown)
    catalog('Otherbrand B95-XL', [{ 'Otherbrand' => 'brand' }, { 'B95' => 'model' }, { 'XL' => 'model' }])
    misspelled = prediction.deep_dup
    misspelled[:breakdown][0] = { 'Zimj' => 'brand' }
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(misspelled)
    expect(described_class.call('Zimj B95-XL-01 White').first[:id]).to eq(xl.id)
  end

  it 'retains fit-related attributes in ranking' do
    source = xl_breakdown + [{ 'Headband' => 'strap' }, { 'N95' => 'filter_type' }, { 'Bifold' => 'style' }]
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(breakdown: source)
    preferred = catalog('Zimi B95-XL Headband', source)
    catalog('Zimi B95-XL Earloop', xl_breakdown + [{ 'Earloop' => 'strap' }])
    expect(described_class.call('Zimi B95-XL Headband N95 Bifold').first[:id]).to eq(preferred.id)
  end

  it 'caches query predictions and invalidates them when the model version changes' do
    catalog('Zimi B95-XL', xl_breakdown)
    2.times { described_class.call(query) }
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).once
    allow(MaskMatching::PredictionCache).to receive(:version).and_return('next-model')
    described_class.call(query)
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).twice
  end

  it 'warms missing catalog classifications asynchronously and deduplicates scheduling' do
    xl = catalog('Zimi B95-XL')
    2.times { expect(described_class.call(query).first[:id]).to eq(xl.id) }
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).with(query, seconds: 5).once
    jobs = enqueued_jobs.select { |job| job[:job] == WarmMaskMatchingCatalogJob }
    expect(jobs.size).to eq(1)
    expect(jobs.first[:args]).to eq([[xl.id]])
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).with(xl.unique_internal_model_code,
                                                                                seconds: 5)
                                                                          .and_return(breakdown: xl_breakdown)
    WarmMaskMatchingCatalogJob.perform_now([xl.id])
    expect(described_class.call(query).first[:score]).to be > 0.8
  end

  it 'prefers saved annotations over cached predictions and falls back to the latest event' do
    xl = catalog('Zimi B95-XL', xl_breakdown)
    cache.write(MaskMatching::PredictionCache.key(xl.unique_internal_model_code),
                { components: { brand: ['Wrong'], model: ['Other'] } })
    expect(described_class.call(query).first[:score]).to be > 0.8
    xl.mask_events.create!(user: admin, event_type: 'breakdown_updated', data: { breakdown: xl_breakdown })
    xl.update!(current_state: {})
    expect(described_class.call(query).first[:score]).to be > 0.8
  end

  it 'falls back to name matching for failed or uninformative predictions' do
    xl = catalog('Zimi B95-XL', xl_breakdown)
    [nil, { fallback: true }, { breakdown: [{ 'White' => 'color' }] }].each do |result|
      cache.clear
      allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(result)
      expect(described_class.call(query).first[:id]).to eq(xl.id)
    end
  end

  it 'briefly caches failed predictions and retries after expiration' do
    allow(MaskComponentPredictorService).to receive(:predict_with_timeout).and_return(nil)
    2.times { MaskMatching::PredictionCache.predict(query) }
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).once
    travel 31.seconds do
      MaskMatching::PredictionCache.predict(query)
    end
    expect(MaskComponentPredictorService).to have_received(:predict_with_timeout).twice
  end

  it 'uses name matching when the classification cache is unavailable' do
    xl = catalog('Zimi B95-XL')
    allow(cache).to receive(:read).and_raise(IOError)
    allow(cache).to receive(:read_multi).and_raise(IOError)
    allow(cache).to receive(:write).and_raise(IOError)
    expect(described_class.call(query).first[:id]).to eq(xl.id)
  end
end
