require 'rails_helper'

RSpec.describe N99ModeToN95ModeConverterService do
  describe '.call' do
    let(:mask) { create(:mask) }
    let(:user) { create(:user) }
    let(:facial_measurement) { create(:facial_measurement, user: user) }

    context 'with N99 fit test data' do
      let!(:fit_test) do
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
                  name: 'Deep breathing',
                  fit_factor: 150
                },
                {
                  name: 'Talking',
                  fit_factor: 100
                }
              ]
            }
          }
        )
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
      let!(:fit_test) do
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
          }
        )
      end

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

      it 'should return empty' do
        result = described_class.call.to_a

        expect(result).to be_empty
      end
    end

    context 'with invalid data' do
      let!(:fit_test) do
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
          }
        )
      end

      it 'should return empty' do
        results = described_class.call.to_a

        expect(results).to be_empty
      end
    end

    context 'with a really low score for exercises but high on the normal breathing (sealed)' do
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
                  fit_factor: 1.5
                },
                {
                  name: 'Bend over',
                  fit_factor: 1.5
                }
              ]
            }
          }
        )
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
          }
        )
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
          }
        )
      end

      it 'returns both' do
        results = described_class.call.to_a

        first_fit_test = results.find{|r| r['id'] == fit_test1.id}
        expect(first_fit_test['qlft_pass']).to be false
        expect(first_fit_test['n']).to be 2
        expect(first_fit_test['n95_mode_hmff']).to be < 5

        second_fit_test = results.find{|r| r['id'] == fit_test2.id}
        expect(second_fit_test['qlft_pass']).to be true
        expect(second_fit_test['n']).to be 1
        expect(second_fit_test['n95_mode_hmff']).to be > 200

        expect(results.length).to eq 2
      end
    end
  end
end
