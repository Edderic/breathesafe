require 'rails_helper'

RSpec.describe N95ModeService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }

  describe '.call' do
    context 'with N95 fit test data' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          quantitative_fit_testing_device: measurement_device,
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 200 },
                { 'name' => 'Deep breathing', 'fit_factor' => 150 },
                { 'name' => 'Head moving', 'fit_factor' => 120 },
                { 'name' => 'Talking', 'fit_factor' => 100 }
              ]
            }
          }
        )
      end

      it 'calculates harmonic mean fit factor correctly' do
        result = described_class.call.to_a.first

        # Harmonic mean calculation:
        # 3 / (1/150 + 1/120 + 1/100) = 3 / (0.00667 + 0.00833 + 0.01) = 3 / 0.025 = 120
        expect(result['n95_mode_hmff']).to be_within(0.1).of(120)
        expect(result['n']).to eq(3) # Excludes 'Normal breathing (SEALED)'
        expect(result['qlft_pass']).to be true # 120 >= 100
      end

      context 'with multiple fit tests for the same mask' do
        let!(:second_fit_test) do
          create(:fit_test,
            user: user,
            mask: mask,
            quantitative_fit_testing_device: measurement_device,
            results: {
              'quantitative' => {
                'testing_mode' => 'N95',
                'exercises' => [
                  { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 180 },
                  { 'name' => 'Deep breathing', 'fit_factor' => 160 },
                  { 'name' => 'Head moving', 'fit_factor' => 140 },
                  { 'name' => 'Talking', 'fit_factor' => 130 }
                ]
              }
            }
          )
        end

        it 'returns results for each fit test' do
          results = described_class.call.to_a
          expect(results.length).to eq(2)
        end
      end
    end

    context 'with failed fit test' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          quantitative_fit_testing_device: measurement_device,
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 200 },
                { 'name' => 'Deep breathing', 'fit_factor' => 80 },
                { 'name' => 'Head moving', 'fit_factor' => 90 },
                { 'name' => 'Talking', 'fit_factor' => 85 }
              ]
            }
          }
        )
      end

      it 'identifies failed fit test' do
        result = described_class.call.to_a.first

        # Harmonic mean calculation:
        # 3 / (1/80 + 1/90 + 1/85) = 3 / (0.0125 + 0.0111 + 0.0118) = 3 / 0.0354 = 84.75
        expect(result['n95_mode_hmff']).to be_within(0.1).of(84.75)
        expect(result['qlft_pass']).to be false # 84.75 < 100
      end
    end

    context 'with edge cases' do
      context 'when fit factors are missing' do
        let!(:fit_test) do
          create(:fit_test,
            user: user,
            mask: mask,
            quantitative_fit_testing_device: measurement_device,
            results: {
              'quantitative' => {
                'testing_mode' => 'N95',
                'exercises' => [
                  { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 200 },
                  { 'name' => 'Deep breathing', 'fit_factor' => nil },
                  { 'name' => 'Head moving', 'fit_factor' => 120 },
                  { 'name' => 'Talking', 'fit_factor' => 100 }
                ]
              }
            }
          )
        end

        it 'excludes exercises with missing fit factors' do
          result = described_class.call.to_a.first
          expect(result['n']).to eq(3) # Only includes exercises with valid fit factors
        end
      end

      context 'when all exercises have the same fit factor' do
        let!(:fit_test) do
          create(:fit_test,
            user: user,
            mask: mask,
            quantitative_fit_testing_device: measurement_device,
            results: {
              'quantitative' => {
                'testing_mode' => 'N95',
                'exercises' => [
                  { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 200 },
                  { 'name' => 'Deep breathing', 'fit_factor' => 100 },
                  { 'name' => 'Head moving', 'fit_factor' => 100 },
                  { 'name' => 'Talking', 'fit_factor' => 100 }
                ]
              }
            }
          )
        end

        it 'calculates correct harmonic mean for identical fit factors' do
          result = described_class.call.to_a.first
          expect(result['n95_mode_hmff']).to be_within(0.1).of(100)
          expect(result['qlft_pass']).to be true # 100 >= 100
        end
      end

      context 'when there are no exercises except Normal breathing (SEALED)' do
        let!(:fit_test) do
          create(:fit_test,
            user: user,
            mask: mask,
            quantitative_fit_testing_device: measurement_device,
            results: {
              'quantitative' => {
                'testing_mode' => 'N95',
                'exercises' => [
                  { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => 200 }
                ]
              }
            }
          )
        end

        it 'returns no results' do
          results = described_class.call.to_a
          expect(results).to be_empty
        end
      end
    end
  end
end
