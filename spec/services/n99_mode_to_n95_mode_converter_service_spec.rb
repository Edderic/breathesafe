# frozen_string_literal: true

require 'rails_helper'

RSpec.describe N99ModeToN95ModeConverterService do
  describe '.call' do
    let(:mask) { create(:mask) }
    let(:user) { create(:user) }
    let(:facial_measurement) do
      create(:facial_measurement, user: user, face_width: 140, jaw_width: 120, face_depth: 110)
    end

    let(:measurement_device) do
      create(:measurement_device)
    end

    let(:exercises) do
      [
        {
          name: 'Normal breathing (SEALED)',
          fit_factor: 200
        },
        {
          name: 'Deep breathing',
          fit_factor: 150
        },
        {
          name: 'Talking',
          fit_factor: 100
        }
      ]
    end

    context 'with N99 fit test data' do
      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end

      let!(:facial_measurement) do
        create(:facial_measurement)
      end

      before do
        fit_test
      end

      it 'includes facial measurements' do
        result = described_class.call.to_a.first

        FacialMeasurement::COLUMNS.each do |col|
          expect(result[col]).to eq(facial_measurement.send(col))
        end
      end

      context 'when facial measurements are missing' do
        let(:facial_measurement) do
          nil
        end

        it 'returns nil for facial measurements' do
          result = described_class.call.to_a.first

          FacialMeasurement::COLUMNS.each do |col|
            expect(result[col]).to be_nil
          end
        end
      end

      it 'calculates N95 mode estimates correctly' do
        result = described_class.call.to_a.first

        expect(result['id']).to eq(fit_test.id)
        expect(result['n']).to eq(1) # Excludes 'Talking', 'Normal breathing (SEALED)'
        # FF = 1 / (1 - FE)
        # 150 = 1 / (1 - FE)
        # 1 - FE = 1 / 150
        # 1 - 1 / 150 = FE = 0.993333333
        #
        # Normal breathing (SEALED)
        # 1 - 1 / 200 = FE = 0.995
        # 1 / (1 - 0.99333333 / 0.995) = 596.98
        # multiply by 2 to increase sensitivity
        #
        # 1193
        expect(result['n95_mode_hmff']).to be > 1193
        expect(result['n95_mode_hmff']).to be <= 1194
        expect(result['qlft_pass']).to be_truthy
      end

      context 'when the exercises has a blank fit factor for the sealed exercise' do
        let(:exercises) do
          [
            {
              name: 'Normal breathing (SEALED)',
              fit_factor: nil
            },
            {
              name: 'Deep breathing',
              fit_factor: 150
            },
            {
              name: 'Talking',
              fit_factor: 100
            }
          ]
        end

        it 'returns the fit test' do
          results = described_class.call.to_a
          result = results.first
          expect(result['qlft_pass']).to be_nil
        end
      end

      context 'with Aaron filtration efficiency data' do
        before do
          mask.update(
            filtration_efficiencies: [
              {
                filtration_efficiency_percent: 99.9,
                filtration_efficiency_notes: 'Aaron test',
                filtration_efficiency_source: 'https://example.com'
              }
            ]
          )
        end

        it 'includes Aaron data in calculations' do
          result = described_class.call.to_a.first

          expect(result['id']).to eq(fit_test.id)
          expect(result['n']).to eq(1)
          expect(result['n95_mode_hmff']).to be >= 399
          expect(result['n95_mode_hmff']).to be <= 400
          #
          # Sealed FF based on Aaron's data'
          # FF = 1 / (1-0.999 FE)
          # FF = 1 / 0.001 = 1000
          #
          # Sealed FF based on test (Normal Breathing (SEALED))
          # FF = 200
          #
          # Avg sealed FF
          # (1000 + 200) / 2 = 600
          #
          # Exclude Talking exercise
          #
          # Deep breathing FF = 150
          # FF = 1 / (1 - FE)
          # 1 - FE = 1 / FF
          # 1 - 1 / FF = FE
          #
          # 1 - 1/ 150 = 0.993333333
          #
          # 1- 1 / 600 = 0.998333333
          #
          # 1 / (1 - 0.993333333 / 0.998333333)
          # = 199.66
          #
          # multiply by 2 to increase sensitivity
          # = 199.66 * 2
        end
      end
    end

    context 'when Normal breathing (SEALED) is the only entry' do
      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: [
                     {
                       name: 'Normal breathing (SEALED)',
                       fit_factor: 200
                     }
                   ]
                 }
               })
      end

      before do
        fit_test

        mask.update(
          filtration_efficiencies: [
            {
              filtration_efficiency_percent: 99.9,
              filtration_efficiency_notes: 'Aaron test',
              filtration_efficiency_source: 'https://example.com'
            }
          ]
        )
      end

      it 'returns empty' do
        result = described_class.call.to_a

        expect(result).to be_empty
      end
    end

    context 'with invalid data' do
      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: [
                     {
                       name: 'Normal breathing (SEALED)',
                       fit_factor: nil
                     }
                   ]
                 }
               })
      end

      before do
        fit_test
      end

      it 'returns empty' do
        results = described_class.call.to_a

        expect(results).to be_empty
      end
    end

    context 'with a really low score for exercises but high on the normal breathing (sealed)' do
      let(:fit_test1) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: [
                     {
                       name: 'Normal breathing (SEALED)',
                       fit_factor: 200
                     },
                     {
                       name: 'Normal breathing',
                       fit_factor: 1.5
                     },
                     {
                       name: 'Bend over',
                       fit_factor: 1.5
                     }
                   ]
                 }
               })
      end

      before do
        fit_test1
      end

      it 'shows failing qlft' do
        result = described_class.call.to_a.first

        expect(result['n95_mode_hmff']).to be < 100
        expect(result['qlft_pass']).to be false
      end
    end

    context 'with multiple fit tests for same mask' do
      let!(:fit_test1) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: [
                     {
                       name: 'Normal breathing (SEALED)',
                       fit_factor: 200
                     },
                     {
                       name: 'Normal breathing',
                       fit_factor: 1
                     },
                     {
                       name: 'Side to side',
                       fit_factor: 1
                     }
                   ]
                 }
               })
      end

      let!(:fit_test2) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: [
                     {
                       name: 'Normal breathing (SEALED)',
                       fit_factor: 300
                     },
                     {
                       name: 'Normal breathing',
                       fit_factor: 299
                     }
                   ]
                 }
               })
      end

      it 'returns both' do
        results = described_class.call.to_a

        first_fit_test = results.find { |r| r['id'] == fit_test1.id }
        expect(first_fit_test['qlft_pass']).to be false
        expect(first_fit_test['n']).to be 2
        expect(first_fit_test['n95_mode_hmff']).to be < 5

        second_fit_test = results.find { |r| r['id'] == fit_test2.id }
        expect(second_fit_test['qlft_pass']).to be true
        expect(second_fit_test['n']).to be 1
        expect(second_fit_test['n95_mode_hmff']).to be > 200

        expect(results.length).to eq 2
      end
    end

    context 'with facial hair data' do
      let(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing (SEALED)',
                       'fit_factor' => '200'
                     },
                     {
                       'name' => 'Deep breathing',
                       'fit_factor' => '150'
                     }
                   ]
                 }
               },
               facial_hair: {
                 'beard_length_mm' => 5
               })
      end

      before do
        fit_test
      end

      it 'includes facial_hair_beard_length_mm in the results' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to eq(5)
      end
    end

    context 'with missing facial hair data' do
      let(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing (SEALED)',
                       'fit_factor' => '200'
                     },
                     {
                       'name' => 'Deep breathing',
                       'fit_factor' => '150'
                     }
                   ]
                 }
               },
               facial_hair: nil)
      end

      before do
        fit_test
      end

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end

    context 'with empty facial hair beard length' do
      let(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing (SEALED)',
                       'fit_factor' => '200'
                     },
                     {
                       'name' => 'Deep breathing',
                       'fit_factor' => '150'
                     }
                   ]
                 }
               },
               facial_hair: {})
      end

      before do
        fit_test
      end

      it 'returns nil for facial_hair_beard_length_mm' do
        result = described_class.call.to_a.first
        expect(result['facial_hair_beard_length_mm']).to be_nil
      end
    end

    context 'with mask_id parameter' do
      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end
      let(:other_mask) { create(:mask) }

      before do
        fit_test
        # Create N99 fit test for other_mask
        create(:fit_test,
               user: user,
               mask: other_mask,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
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
               })
      end

      it 'returns all N99 fit tests converted to N95 mode when no mask_id is provided' do
        results = described_class.call
        expect(results.count).to eq(2)
        expect(results.map { |r| r['mask_id'] }).to contain_exactly(mask.id, other_mask.id)
      end

      it 'returns only fit tests for the specified mask when mask_id is provided' do
        results = described_class.call(mask_id: mask.id)
        expect(results.count).to eq(1)
        expect(results.first['mask_id']).to eq(mask.id)
      end
    end

    context 'with z-score computation' do
      let(:facial_measurement) do
        create(:facial_measurement, user: user, face_width: 140, jaw_width: 120, face_depth: 110)
      end

      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end

      before do
        fit_test
      end

      it 'computes z-scores for facial measurements' do
        result = described_class.call.to_a.first
        FacialMeasurement::COLUMNS.each do |col|
          z_score_col = "#{col}_z_score"
          expect(result).to have_key(z_score_col)
          # With only one measurement, stddev will be 0, so z-score should be nil
          expect(result[z_score_col]).to be_nil
        end
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

      let(:fit_test2) do
        create(:fit_test,
               mask: mask,
               user: user2,
               facial_measurement: facial_measurement2,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end

      let(:fit_test1) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end

      before do
        fit_test1
        fit_test2
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

    context 'when facial measurements are missing' do
      let(:facial_measurement) { nil }

      let(:fit_test) do
        create(:fit_test,
               mask: mask,
               user: user,
               facial_measurement: facial_measurement,
               results: {
                 quantitative: {
                   testing_mode: 'N99',
                   exercises: exercises
                 }
               })
      end

      before do
        fit_test
      end

      it 'returns nil for z-score columns' do
        result = described_class.call.to_a.first
        FacialMeasurement::COLUMNS.each do |col|
          z_score_col = "#{col}_z_score"
          expect(result[z_score_col]).to be_nil
        end
      end
    end
  end
end
