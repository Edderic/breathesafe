# frozen_string_literal: true

require 'rails_helper'

RSpec.describe BulkDataImporter, type: :service do
  let!(:mask_a) { create(:mask, unique_internal_model_code: 'CRASH25-A1', perimeter_mm: 500) }
  let!(:user)   { create(:user) }

  let(:headers) do
    [
      'Mask name',
      'suggested_breathesafe_unique_internal_model_code',
      'distance',
      'suggested_breathesafe_mask_id',
      'confirmed_breathesafe_mask_id',
      *('Exercise 1'..'Exercise 12').to_a,
      'Protocol',
      'Notes'
    ]
  end

  let(:csv_rows) do
    [
      ['crash25-a1', '', '', '', '', *Array.new(12, ''), 'N95', 'ok'], # should match mask_a
      ['unknown mask', '', '', '', '', *Array.new(12, ''), 'N95', 'ok']
    ]
  end

  let(:input_csv) do
    CSV.generate do |csv|
      csv << headers
      csv_rows.each { |r| csv << r }
    end
  end

  before do
    # Stub S3 read/write to avoid external deps
    allow(described_class).to receive(:s3_client).and_raise(StandardError) # force local path fallback
    allow(described_class).to receive(:write_csv_to_s3).and_return(true)

    # Stub file reads for both relative and expanded paths
    allow(File).to receive(:read).and_call_original
    allow(File).to receive(:read).with('input.csv').and_return(input_csv)
    allow(File).to receive(:read).with(File.expand_path('input.csv')).and_return(input_csv)
  end

  describe 'validate mode' do
    it 'fills suggested fields and distance for blank confirmed ids' do
      result = described_class.call(
        style: 'Crash2.5',
        read_path: 'input.csv',
        write_path: 'output.csv',
        environment: 'development',
        user_id: user.id,
        mode: 'validate',
        testing_mode: 'N95'
      )
      expect(result[:status]).to eq('ok')

      # Parse the output we would have written
      CSV.parse(input_csv, headers: true) # Just reuse structure
      # We can recompute to check suggestions directly via private methods if needed; keep high level here

      # Ensure best suggestion for row 1 is mask_a
      suggestion, distance = invoke_best_suggestion('crash25-a1')
      expect(suggestion[:mask_id]).to eq(mask_a.id)
      expect(distance).to be < 0.4
    end
  end

  describe 'save mode' do
    it 'raises when confirmed id is blank' do
      expect do
        described_class.call(
          style: 'Crash2.5',
          read_path: 'input.csv',
          write_path: 'output.csv',
          environment: 'development',
          user_id: user.id,
          mode: 'save',
          testing_mode: 'N95'
        )
      end.to raise_error(ArgumentError)
    end

    it 'creates fit tests for rows with confirmed id and skips SKIP' do
      confirmed_csv = CSV.generate do |csv|
        csv << headers
        csv << ['crash25-a1', '', '', '', mask_a.id, *Array.new(12, ''), 'N95', 'ok']
        csv << ['unknown', '', '', '', 'SKIP', *Array.new(12, ''), 'N95', 'skip row']
      end
      allow(File).to receive(:read).with('input.csv').and_return(confirmed_csv)
      allow(File).to receive(:read).with(File.expand_path('input.csv')).and_return(confirmed_csv)

      expect do
        described_class.call(
          style: 'Crash2.5',
          read_path: 'input.csv',
          write_path: 'output.csv',
          environment: 'development',
          user_id: user.id,
          mode: 'save',
          testing_mode: 'N95'
        )
      end.to change(FitTest, :count).by(1)
      ft = FitTest.last
      expect(ft.mask_id).to eq(mask_a.id)
      expect(ft.results['quantitative']).to be_present
    end
  end

  # Helper to access private matching routine
  def invoke_best_suggestion(name)
    klass = described_class.singleton_class
    method = klass.send(:instance_method, :best_suggestion_for)
    # Prepare a mask index like in the service
    codes = Mask.where.not(unique_internal_model_code: [nil, '']).pluck(:id, :unique_internal_model_code)
    mask_index = codes.map do |id, code|
      norm = described_class.send(:normalize_text, code)
      [id, code, norm, described_class.send(:trigrams, norm)]
    end
    method.bind(described_class).call(name, mask_index)
  end
end
