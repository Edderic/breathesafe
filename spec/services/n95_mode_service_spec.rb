require 'rails_helper'

RSpec.describe N95ModeService do
  let(:user) { create(:user) }
  let(:mask) { create(:mask) }
  let(:measurement_device) { create(:measurement_device, :digital_caliper) }
  let(:facial_measurement) { create(:facial_measurement, :complete, user: user) }

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
         },
         facial_measurement: facial_measurement
        )
      end

      it "has the facial_measurement data associated to it" do
        result = described_class.call.to_a.first
        FacialMeasurement::COLUMNS.each do |col|
          expect(result[col]).to eq(facial_measurement.send(col))
        end
      end

      it 'calculates harmonic mean fit factor correctly' do
        result = described_class.call.to_a.first

        # Harmonic mean calculation:
        # 3 / (1/150 + 1/120 + 1/100) = 3 / (0.00667 + 0.00833 + 0.01) = 3 / 0.025 = 120
        expect(result['n95_mode_hmff']).to be_within(0.1).of(120)
        expect(result['n']).to eq(3) # Excludes 'Normal breathing (SEALED)'
        expect(result['qlft_pass']).to be true # 120 >= 100
      end

      context "when facial measurements are missing" do
        let(:facial_measurement) do
          nil
        end

        it "returns nil for each of the facial measurements" do
          result = described_class.call.to_a.first
          FacialMeasurement::COLUMNS.each do |col|
            expect(result[col]).to be nil
          end
        end
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

    context 'with facial hair data' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          quantitative_fit_testing_device: measurement_device,
          facial_measurement: facial_measurement,
          facial_hair: {
            'beard_length_mm' => 5,
            'other_field' => 'value'
          },
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

      it 'includes facial_hair_beard_length_mm' do
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
          facial_hair: nil,
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
          facial_hair: {
            'beard_length_mm' => nil,
            'other_field' => 'value'
          },
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

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end

    context 'with optional mask_id parameter' do
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
         },
         facial_measurement: facial_measurement
        )
      end

      let(:other_mask) { create(:mask) }

      before do
        # Create N95 fit test for other_mask
        create(:fit_test,
          user: user,
          mask: other_mask,
          facial_measurement: facial_measurement,
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                {
                  'name' => 'Normal breathing (SEALED)',
                  'fit_factor' => '180'
                },
                {
                  'name' => 'Bending over',
                  'fit_factor' => '120'
                }
              ]
            }
          }
        )
      end

      it 'returns all N95 fit tests when no mask_id is provided' do
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

    context 'when beard_length_mm is "1mm"' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          quantitative_fit_testing_device: measurement_device,
          facial_hair: { beard_length_mm: "1mm" },
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                {
                  'name' => 'Normal breathing',
                  'fit_factor' => '200'
                }
              ]
            }
          }
        )
      end

      it 'returns 0 for facial_hair_beard_length_mm' do
        result = described_class.call(mask_id: mask.id).to_a.first
        expect(result['facial_hair_beard_length_mm']).to eq(1)
      end
    end

    context 'when beard_length_mm is "5mm"' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          quantitative_fit_testing_device: measurement_device,
          facial_hair: { beard_length_mm: "5mm" },
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                {
                  'name' => 'Normal breathing',
                  'fit_factor' => '200'
                }
              ]
            }
          }
        )
      end

      it 'returns 5 for facial_hair_beard_length_mm' do
        result = described_class.call(mask_id: mask.id).to_a.first
        expect(result['facial_hair_beard_length_mm']).to eq(5)
      end
    end

    context 'when beard_length_mm is nil' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          quantitative_fit_testing_device: measurement_device,
          facial_hair: { beard_length_mm: nil },
          results: {
            'quantitative' => {
              'testing_mode' => 'N95',
              'exercises' => [
                {
                  'name' => 'Normal breathing',
                  'fit_factor' => '200'
                }
              ]
            }
          }
        )
      end

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call(mask_id: mask.id).to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end
  end
end
