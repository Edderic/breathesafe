require 'rails_helper'

RSpec.describe FitTestsWithFacialMeasurementsService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }
  let(:facial_measurement) { create(:facial_measurement, :complete, user: user) }

  describe '.call' do
    context 'with all types of fit tests' do
      let!(:n95_fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          quantitative_fit_testing_device: measurement_device,
          facial_measurement: facial_measurement,
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                { 'name' => 'Exercise 1', 'fit_factor' => '200' },
                { 'name' => 'Exercise 2', 'fit_factor' => '300' },
                { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => '400' }
              ]
            }
          }
        )
      end

      let!(:n99_fit_test) do
        create(:fit_test,
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
          }
        )
      end

      let!(:qlft_test) do
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
          }
        )
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
          }
        )
      end

      let!(:failing_qlft_test) do
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
          }
        )
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
      let!(:fit_test_without_measurements) do
        create(:fit_test,
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
          }
        )
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
