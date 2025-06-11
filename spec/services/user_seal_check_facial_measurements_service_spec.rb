require 'rails_helper'

RSpec.describe UserSealCheckFacialMeasurementsService do
  describe '.call' do
    let(:user) { create(:user) }
    let(:mask) { create(:mask) }
    let(:other_mask) { create(:mask) }
    let(:facial_measurement) { create(:facial_measurement, user: user) }

    context 'with user seal check data' do
      let!(:fit_test_too_small) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Too small'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => nil
            }
          }
        )
      end

      let!(:fit_test_too_big) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Too big'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => nil
            }
          }
        )
      end

      let!(:fit_test_lot_of_air) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Just right'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => 'A lot of air movement'
            }
          }
        )
      end

      let!(:fit_test_pass) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Just right'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
            }
          }
        )
      end

      it 'returns all fit tests with correct qlft_pass values' do
        results = described_class.call
        expect(results.count).to eq(4)

        # Find results by mask_id and check qlft_pass
        too_small_result = results.find { |r| r['id'] == fit_test_too_small.id }
        too_big_result = results.find { |r| r['id'] == fit_test_too_big.id }
        lot_of_air_result = results.find { |r| r['id'] == fit_test_lot_of_air.id }
        pass_result = results.find { |r| r['id'] == fit_test_pass.id }

        expect(too_small_result['qlft_pass']).to be false
        expect(too_big_result['qlft_pass']).to be false
        expect(lot_of_air_result['qlft_pass']).to be false
        expect(pass_result['qlft_pass']).to be nil
      end

      it 'includes facial measurements' do
        results = described_class.call
        result = results.first

        FacialMeasurement::COLUMNS.each do |column|
          expect(result).to have_key(column)
        end
      end
    end

    context 'with optional mask_id parameter' do
      let!(:fit_test) do
        create(:fit_test,
          user: user,
          mask: mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Too small'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => nil
            }
          }
        )
      end

      let(:other_mask) { create(:mask) }

      let!(:other_fit_test) do
        create(:fit_test,
          user: user,
          mask: other_mask,
          facial_measurement: facial_measurement,
          user_seal_check: {
            'sizing' => {
              'What do you think about the sizing of this mask relative to your face?' => 'Too small'
            },
            'negative' => {
              '...how much air passed between your face and the mask?' => nil
            },
            'positive' => {
              '...how much did your glasses fog up?' => nil,
              '...how much pressure build up was there?' => nil,
              '...how much air movement on your face along the seal of the mask did you feel?' => nil
            }
          }
        )
      end

      it 'returns all fit tests when no mask_id is provided' do
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
