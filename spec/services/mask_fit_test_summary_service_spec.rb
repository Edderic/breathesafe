# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskFitTestSummaryService do
  describe '.call' do
    let(:manager) { create(:user) }
    let(:managed_user) { create(:user) }
    let(:fit_family) { create(:fit_family) }
    let(:mask_a) { create(:mask, fit_family: fit_family, unique_internal_model_code: 'TRIDENT-S-WHITE') }
    let(:mask_b) { create(:mask, fit_family: fit_family, unique_internal_model_code: 'TRIDENT-S-BLACK') }

    before do
      create(:managed_user, manager: manager, managed: managed_user)
      create(:facial_measurement, user: managed_user)

      allow(FitTestsWithFacialMeasurementsService).to receive(:call).and_return(
        [
          {
            'id' => 1,
            'user_id' => managed_user.id,
            'mask_id' => mask_a.id,
            'fit_family_id' => fit_family.id,
            'qlft_pass' => false,
            'created_at' => 1.day.ago.iso8601
          },
          {
            'id' => 2,
            'user_id' => managed_user.id,
            'mask_id' => mask_b.id,
            'fit_family_id' => fit_family.id,
            'qlft_pass' => true,
            'created_at' => Time.current.iso8601
          }
        ]
      )
    end

    it 'aggregates observed fit summaries across all masks in the same fit family' do
      result = described_class.call(
        viewer: manager,
        target_user_id: managed_user.id,
        mask_ids: [mask_a.id, mask_b.id]
      )

      expect(result[mask_a.id]['observed_fit_test_count']).to eq(2)
      expect(result[mask_a.id]['observed_fit_pass_count']).to eq(1)
      expect(result[mask_a.id]['observed_fit_pass_rate']).to eq(0.5)

      expect(result[mask_b.id]).to eq(result[mask_a.id])
    end
  end
end
