# frozen_string_literal: true

require 'rails_helper'

RSpec.describe QlftService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }
  let(:facial_measurement) do
    create(:facial_measurement, :complete, user: user, face_width: 140, jaw_width: 120, face_depth: 110)
  end

  let(:exercises) do
    [
      { 'name' => 'Exercise 1', 'result' => 'Pass' },
      { 'name' => 'Exercise 2', 'result' => 'Pass' },
      { 'name' => 'Exercise 3', 'result' => 'Pass' }
    ]
  end

  describe '.call' do
    context 'with passing qualitative fit test' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => exercises
                 }
               })
      end

      it 'returns passing result with facial measurements' do
        result = described_class.call.to_a.first

        expect(result['qlft_pass']).to be true
        expect(result['n']).to be exercises.length
        expect(result['denominator']).to be_nil
        expect(result['n95_mode_hmff']).to be_nil
        expect(result['face_width']).to eq(facial_measurement.face_width)
        expect(result['jaw_width']).to eq(facial_measurement.jaw_width)
      end

      it 'computes z-scores for facial measurements' do
        result = described_class.call.to_a.first

        # Check that z-score columns exist
        FacialMeasurement::COLUMNS.each do |col|
          z_score_col = "#{col}_z_score"
          expect(result).to have_key(z_score_col)

          # If the measurement value exists, z-score should be computed
          if facial_measurement.send(col).present?
            # With only one measurement, stddev will be 0, so z-score should be null
          end
          expect(result[z_score_col]).to be_nil
        end
      end
    end

    context 'with failing qualitative fit test' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Fail' },
                     { 'name' => 'Exercise 3', 'result' => 'Pass' }
                   ]
                 }
               })
      end

      it 'returns failing result' do
        result = described_class.call.to_a.first
        expect(result['qlft_pass']).to be false
      end
    end

    context 'with mixed results' do
      context 'when some results are null or blank' do
        let!(:fit_test) do
          create(:fit_test,
                 user: user,
                 mask: mask,
                 quantitative_fit_testing_device: measurement_device,
                 facial_measurement: facial_measurement,
                 results: {
                   'qualitative' => {
                     'exercises' => [
                       { 'name' => 'Exercise 1', 'result' => 'Pass' },
                       { 'name' => 'Exercise 2', 'result' => nil },
                       { 'name' => 'Exercise 3', 'result' => '' }
                     ]
                   }
                 })
        end

        it 'treats null/blank results as passing' do
          result = described_class.call.to_a.first
          expect(result['qlft_pass']).to be true
        end
      end

      context 'when there are no explicit passes' do
        let!(:fit_test) do
          create(:fit_test,
                 user: user,
                 mask: mask,
                 quantitative_fit_testing_device: measurement_device,
                 facial_measurement: facial_measurement,
                 results: {
                   'qualitative' => {
                     'exercises' => [
                       { 'name' => 'Exercise 1', 'result' => nil },
                       { 'name' => 'Exercise 2', 'result' => '' },
                       { 'name' => 'Exercise 3', 'result' => nil }
                     ]
                   }
                 })
        end

        it 'returns null for qlft_pass' do
          result = described_class.call.to_a.first
          expect(result['qlft_pass']).to be_nil
        end
      end
    end

    context 'with multiple fit tests' do
      let!(:passing_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Pass' }
                   ]
                 }
               })
      end

      let!(:failing_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Fail' }
                   ]
                 }
               })
      end

      it 'returns results for all fit tests' do
        results = described_class.call.to_a
        expect(results.length).to eq(2)

        passing_result = results.find { |r| r['id'] == passing_test.id }
        failing_result = results.find { |r| r['id'] == failing_test.id }

        expect(passing_result['qlft_pass']).to be true
        expect(failing_result['qlft_pass']).to be false
      end
    end

    context 'with multiple users for z-score calculation' do
      let(:user2) { create(:user) }

      let!(:facial_measurement2) do
        create(:facial_measurement,
               user: user2,
               face_width: 150, # Different value for z-score calculation
               jaw_width: 130,
               face_depth: 120)
      end

      let!(:fit_test2) do
        create(:fit_test,
               user: user2,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement2,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Pass' }
                   ]
                 }
               })
      end

      let!(:fit_test1) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Pass' }
                   ]
                 }
               })
      end

      it 'computes z-scores based on population statistics' do
        results = described_class.call.to_a
        expect(results.length).to eq(2)

        # Find the result for the original user
        original_result = results.find { |r| r['user_id'] == user.id }

        # The z-scores should be computed based on the population of 2 users
        # For face_width: values are 140, 150
        # Mean = 145, StdDev = sqrt(sum((x-mean)^2)/n) = sqrt(50/2) = 5
        # Original user (140) should have z-score = (140-145)/5 = -1.0
        expect(original_result['face_width_z_score']).to be_within(0.1).of(-1.0)
      end
    end

    context 'with missing facial measurements' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'result' => 'Pass' },
                     { 'name' => 'Exercise 2', 'result' => 'Pass' }
                   ]
                 }
               },
               facial_measurement: nil)
      end

      it 'returns null for facial measurement fields' do
        result = described_class.call.to_a.first
        expect(result['qlft_pass']).to be true
        expect(result['face_width']).to be_nil
        expect(result['jaw_width']).to be_nil
      end

      it 'returns null for z-score fields when facial measurements are missing' do
        result = described_class.call.to_a.first
        FacialMeasurement::COLUMNS.each do |col|
          z_score_col = "#{col}_z_score"
          expect(result[z_score_col]).to be_nil
        end
      end
    end

    context 'with facial hair data' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'result' => 'Pass'
                     },
                     {
                       'name' => 'Deep breathing',
                       'result' => 'Pass'
                     }
                   ]
                 }
               },
               facial_hair: {
                 'beard_length_mm' => 5
               })
      end

      it 'includes facial_hair_beard_length_mm in the results' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to eq(5)
      end
    end

    context 'with missing facial hair data' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'result' => 'Pass'
                     },
                     {
                       'name' => 'Deep breathing',
                       'result' => 'Pass'
                     }
                   ]
                 }
               },
               facial_hair: nil)
      end

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end

    context 'with empty facial hair beard length' do
      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'result' => 'Pass'
                     },
                     {
                       'name' => 'Deep breathing',
                       'result' => 'Pass'
                     }
                   ]
                 }
               },
               facial_hair: {})
      end

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end

    context 'with optional mask_id parameter' do
      let(:other_mask) { create(:mask) }

      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => exercises
                 }
               })
      end

      before do
        # Create qualitative fit test for other_mask
        create(:fit_test,
               user: user,
               mask: other_mask,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'result' => 'Pass'
                     },
                     {
                       'name' => 'Bending over',
                       'result' => 'Pass'
                     }
                   ]
                 }
               })
      end

      it 'returns all qualitative fit tests when no mask_id is provided' do
        results = described_class.call
        expect(results.count).to eq(2)
        expect(results.map { |r| r['mask_id'] }).to match_array([mask.id, other_mask.id])
      end

      it 'returns only fit tests for the specified mask when mask_id is provided' do
        results = described_class.call(mask_id: mask.id)
        expect(results.count).to eq(1)
        expect(results.first['mask_id']).to eq(mask.id)
      end
    end
  end
end
