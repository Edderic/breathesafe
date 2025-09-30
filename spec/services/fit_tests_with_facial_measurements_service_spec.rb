# frozen_string_literal: true

require 'rails_helper'

RSpec.describe FitTestsWithFacialMeasurementsService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }
  let(:facial_measurement) { create(:facial_measurement, :complete, user: user) }

  describe '.call' do
    context '3M 1870+ AURA N99 to N95 conversion' do
      let(:special_mask) { create(:mask, unique_internal_model_code: '3M 1870+ AURA™') }

      let!(:n99_fit_test_for_3m_1870) do
        create(
          :fit_test,
          :with_just_right_mask,
          user: user,
          mask: special_mask,
          quantitative_fit_testing_device: measurement_device,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' =>
                'Somewhere in-between too small and too big'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => 'Not at all',
              '...how much pressure build up was there?' => 'As expected',
              '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
            }
          },
          comfort: {
            'Is there enough room to talk?' => 'Enough',
            'Is there adequate room for eye protection?' => 'Adequate',
            'How comfortable is the position of the mask on the nose?' => 'Comfortable',
            'How comfortable is the position of the mask on face and cheeks?' => 'Comfortable'
          },
          facial_hair: {
            'beard_length_mm' => '1.5mm',
            'beard_cover_technique' => 'No'
          },
          results: {
            'qualitative' => {
              'aerosol' => { 'solution' => 'Saccharin' },
              'exercises' => [
                { 'name' => 'Normal breathing', 'result' => nil },
                { 'name' => 'Deep breathing', 'result' => nil },
                { 'name' => 'Turning head side to side', 'result' => nil },
                { 'name' => 'Moving head up and down', 'result' => nil },
                { 'name' => 'Talking', 'result' => nil },
                { 'name' => 'Bending over', 'result' => nil },
                { 'name' => 'Normal breathing', 'result' => nil }
              ],
              'procedure' => 'Skipping'
            },
            'quantitative' => {
              'aerosol' => { 'solution' => 'Ambient', 'initial_count_per_cm3' => 2000 },
              'exercises' => [
                { 'name' => 'Normal breathing', 'fit_factor' => 232 },
                { 'name' => 'Deep breathing', 'fit_factor' => 253 },
                { 'name' => 'Turning head side to side', 'fit_factor' => 116 },
                { 'name' => 'Moving head up and down', 'fit_factor' => 151 },
                { 'name' => 'Talking', 'fit_factor' => 133 },
                { 'name' => 'Grimace', 'fit_factor' => 78 },
                { 'name' => 'Bending over', 'fit_factor' => 262 },
                { 'name' => 'Normal breathing', 'fit_factor' => 190 },
                { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 292 }
              ],
              'procedure' => 'Full OSHA',
              'testing_mode' => 'N99'
            }
          }
        )
      end

      it 'converts N99 test to N95 HMFF > 100 and qlft_pass true' do
        results = described_class.call.to_a
        row = results.find { |r| r['id'] == n99_fit_test_for_3m_1870.id && r['source'] == 'N99ModeToN95ModeConverterService' }
        expect(row).not_to be_nil
        expect(row['n95_mode_hmff']).to be > 100
        expect(row['qlft_pass']).to be true
        expect(row['unique_internal_model_code']).to eq('3M 1870+ AURA™')
      end
    end
    context 'with all types of fit tests' do
      let!(:n95_fit_test) do
        create(:fit_test,
               # passes user seal check
               :with_just_right_mask,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 # Passing scores
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'fit_factor' => '200' },
                     { 'name' => 'Exercise 2', 'fit_factor' => '300' },
                     { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => '400' }
                   ]
                 }
               })
      end

      let!(:n99_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'fit_factor' => '200' },
                     { 'name' => 'Exercise 2', 'fit_factor' => '300' },
                     { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => '400' }
                   ]
                 }
               })
      end

      let!(:qlft_test) do
        create(:fit_test,
               :with_just_right_mask,
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

      it 'combines results from all services' do
        results = described_class.call.to_a
        expect(results.length).to eq(3)

        n95_result = results.find { |r| r['id'] == n95_fit_test.id }
        n99_result = results.find { |r| r['id'] == n99_fit_test.id }
        qlft_result = results.find { |r| r['id'] == qlft_test.id }

        # Verify N95 test results
        expect(n95_result['n95_mode_hmff']).to be > 100
        expect(n95_result['qlft_pass']).to be true
        expect(n95_result['face_width']).to eq(facial_measurement.face_width)

        # Verify N99 test results
        expect(n99_result['n95_mode_hmff']).to be > 100
        expect(n99_result['qlft_pass']).to be true
        expect(n99_result['face_width']).to eq(facial_measurement.face_width)

        # Verify QLFT test results
        expect(qlft_result['qlft_pass']).to be true
        expect(qlft_result['n']).to eq(2) # Number of exercises
        expect(qlft_result['face_width']).to eq(facial_measurement.face_width)
      end
    end

    context 'with failing tests' do
      let!(:failing_n95_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'fit_factor' => '50' },
                     { 'name' => 'Exercise 2', 'fit_factor' => '60' },
                     { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => '70' }
                   ]
                 }
               })
      end

      let!(:failing_qlft_test) do
        create(:fit_test,
               :with_just_right_mask,
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

      it 'includes failing test results' do
        results = described_class.call.to_a
        expect(results.length).to eq(2)

        n95_result = results.find { |r| r['id'] == failing_n95_test.id }
        qlft_result = results.find { |r| r['id'] == failing_qlft_test.id }

        expect(n95_result['n95_mode_hmff']).to be < 100
        expect(n95_result['qlft_pass']).to be false
        expect(qlft_result['qlft_pass']).to be false
      end
    end

    context 'with missing facial measurements' do
      let(:fit_test_without_measurements) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               mask: mask,
               facial_measurement: nil,
               quantitative_fit_testing_device: measurement_device,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     { 'name' => 'Exercise 1', 'fit_factor' => '200' },
                     { 'name' => 'Exercise 2', 'fit_factor' => '300' }
                   ]
                 }
               })
      end

      before do
        fit_test_without_measurements
      end

      it 'returns results with null facial measurements' do
        results = described_class.call.to_a
        expect(results.length).to eq(1)

        result = results.first
        expect(result['n95_mode_hmff']).to be > 100
        expect(result['face_width']).to be_nil
        expect(result['jaw_width']).to be_nil
      end
    end

    context 'with no fit tests' do
      it 'returns empty array' do
        results = described_class.call.to_a
        expect(results).to be_empty
      end
    end
  end
end
