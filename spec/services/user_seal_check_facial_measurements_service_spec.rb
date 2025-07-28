# frozen_string_literal: true

require 'rails_helper'

RSpec.describe UserSealCheckFacialMeasurementsService do
  describe '.call' do
    let(:user) { create(:user) }
    let(:mask) { create(:mask) }
    let(:other_mask) { create(:mask) }
    let(:facial_measurement) do
      create(:facial_measurement, user: user, face_width: 140, jaw_width: 120, face_depth: 110)
    end

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
               })
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
               })
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
               })
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
               })
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

    context 'with multiple users for z-score calculation' do
      let(:user2) { create(:user) }

      let!(:facial_measurement2) do
        create(:facial_measurement,
               user: user2,
               face_width: 150, # Different value for z-score calculation
               jaw_width: 130,
               face_depth: 120)
      end

      let!(:fit_test1) do
        create(:fit_test,
               user: user,
               mask: mask,
               facial_measurement: facial_measurement,
               user_seal_check: {
                 'sizing' => {
                   'What do you think about the sizing of this mask relative to your face?' => 'Just right'
                 },
                 'positive' => {
                   '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
                 }
               })
      end

      let!(:fit_test2) do
        create(:fit_test,
               user: user2,
               mask: mask,
               facial_measurement: facial_measurement2,
               user_seal_check: {
                 'sizing' => {
                   'What do you think about the sizing of this mask relative to your face?' => 'Just right'
                 },
                 'positive' => {
                   '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
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
      let(:facial_measurement) { nil }

      let!(:fit_test) do
        create(:fit_test,
               user: user,
               mask: mask,
               facial_measurement: facial_measurement,
               user_seal_check: {
                 'sizing' => {
                   'What do you think about the sizing of this mask relative to your face?' => 'Just right'
                 },
                 'positive' => {
                   '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
                 }
               })
      end

      it 'returns null for facial measurement fields' do
        result = described_class.call.to_a.first
        expect(result['qlft_pass']).to be_nil
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
               })
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
               })
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
