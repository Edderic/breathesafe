# frozen_string_literal: true

require 'spec_helper'
require_relative '../../app/services/dashboard_pass_rates_service'

RSpec.describe DashboardPassRatesService do
  def row(user, mask, outcome, family: mask, style: 'Bifold')
    { 'user_id' => user, 'mask_id' => mask, 'fit_family_id' => family, 'style' => style,
      'strap_type' => 'Headstrap', 'unique_internal_model_code' => "Mask #{mask}", 'qlft_pass' => outcome }
  end

  it 'retains per-test rates while giving a prolific tester only one pair vote' do
    data = Array.new(9) { row(1, 10, true) } + [row(2, 10, false)]
    result = described_class.call(data)
    expect(result[:overall]).to eq(total: 10, passed: 9, pass_rate: 90.0)
    expect(result.dig(:equal_person_mask, :overall)).to include(pair_count: 2, pass_rate: 50.0, test_count: 10)
    expect(result.dig(:equal_person_mask, :by_mask).first).to include(name: 'Mask 10', pass_rate: 50.0)
  end

  it 'averages conflicting observations within a pair instead of selecting a favorable outcome' do
    data = [row(1, 10, true)] + Array.new(3) { row(1, 10, false) } + [row(2, 10, true)]
    result = described_class.call(data)
    expect(result.dig(:equal_person_mask, :overall)).to include(pass_rate: 62.5, mixed_pairs: 1)
    expect(result[:overall][:pass_rate]).to eq(40.0)
  end

  it 'averages mask-family rates equally within a style despite unequal numbers of testers' do
    data = (1..4).map { |user| row(user, 10, true) } + [row(5, 20, false)]
    result = described_class.call(data)
    expect(result[:by_style].first[:pass_rate]).to eq(80.0)
    expect(result[:equal_family_by_style].first).to include(
      pass_rate: 50.0, family_count: 2, unique_users: 5, person_family_count: 5, pair_count: 5
    )
  end

  it 'balances variants within a person and people within a shared fit family before averaging styles' do
    data = Array.new(10) { row(1, 10, true, family: 7) } +
           Array.new(2) { row(1, 11, false, family: 7) } + [row(2, 10, true, family: 7)]
    result = described_class.call(data)
    expect(result.dig(:equal_person_mask, :overall)).to include(pair_count: 3, pass_rate: 66.67)
    expect(result[:equal_family_by_style].first).to include(pass_rate: 75.0, family_count: 1, person_family_count: 2)
    expect(result[:equal_family_by_style].first[:families].first).to include(mask_count: 2, pass_rate: 75.0)
  end

  it 'does not group all missing family IDs together or collide a fallback mask with a family ID' do
    data = [row(1, 7, true, family: nil), row(2, 8, false, family: nil), row(3, 9, false, family: 7)]
    result = described_class.call(data)[:equal_family_by_style].first
    expect(result).to include(family_count: 3, pass_rate: 33.33)
    expect(result[:families].map { |family| family[:family_key] }).to contain_exactly('mask:7', 'mask:8', 'family:7')
  end

  it 'excludes missing identities and unlabeled records without inventing pairs or zero-valued empty rates' do
    result = described_class.call([row(nil, 1, true), row(1, nil, false), row(2, 1, nil)])
    expect(result.dig(:equal_person_mask, :overall)).to include(pair_count: 0, pass_rate: nil)
    expect(result[:weighting][:excluded_pair_records]).to eq(2)
    expect(result[:equal_family_by_style]).to be_empty
  end

  it 'handles PostgreSQL boolean strings, canonical numeric/string IDs, and separate styles' do
    data = [row(1, 10, 't'), row('1', '10', 'f'), row(2, 20, false, style: 'Cup')]
    result = described_class.call(data)
    expect(result.dig(:equal_person_mask, :overall)).to include(pair_count: 2, pass_rate: 25.0)
    expect(result[:equal_family_by_style].map { |style| [style[:name], style[:pass_rate]] }).to eq(
      [['Bifold', 50.0], ['Cup', 0.0]]
    )
  end
end
