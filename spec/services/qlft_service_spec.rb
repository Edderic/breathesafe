require 'rails_helper'

RSpec.describe QlftService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }
  let(:facial_measurement) { create(:facial_measurement, :complete, user: user) }

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
          }
        )
      end

      let(:exercises) do
        [
          { 'name' => 'Exercise 1', 'result' => 'Pass' },
          { 'name' => 'Exercise 2', 'result' => 'Pass' },
          { 'name' => 'Exercise 3', 'result' => 'Pass' }
        ]
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
          }
        )
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
            }
          )
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
            }
          )
        end

        it 'returns null for qlft_pass' do
          result = described_class.call.to_a.first
          debugger
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
          }
        )
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
          }
        )
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
          }
        )
      end

      it 'returns null for facial measurement fields' do
        result = described_class.call.to_a.first
        expect(result['qlft_pass']).to be true
        expect(result['face_width']).to be_nil
        expect(result['jaw_width']).to be_nil
      end
    end
  end
end
