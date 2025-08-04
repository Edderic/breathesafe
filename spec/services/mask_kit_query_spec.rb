# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskKitQuery do
  describe '.managed_by' do
    let(:manager) { create(:user) }
    let(:managed_user) { create(:user) }
    let(:mask) { create(:mask, author: manager) }
    let!(:profile) { create(:profile, user: managed_user) }
    let!(:mask_kit_status) do
      create(:mask_kit_status, mask_uuid: mask.id)
    end

    let!(:shipping_status) do
      create(:shipping_status, to_user_uuid: manager.email)
    end

    let(:shipping_status_join) do
      create(:shipping_status_join,
             shipping_uuid: shipping_status.uuid,
             shippable_uuid: mask_kit_status.uuid,
             shippable_type: 'MaskKitStatus')
    end

    before do
      # Create managed user relationship
      ManagedUser.create!(manager: manager, managed: managed_user)
      shipping_status_join
    end

    context 'when user is not an admin' do
      it 'returns masks managed by the specified manager' do
        result = described_class.managed_by(manager_id: manager.id)

        expect(result).to be_an(Array)
        expect(result.first['id']).to eq(mask.id)
        expect(result.first['email']).to eq(manager.email)
        expect(result.first['first_name']).to eq(profile.first_name)
        expect(result.first['last_name']).to eq(profile.last_name)
      end

      it 'includes fit test counts' do
        create(:fit_test, mask: mask, user: managed_user)
        create(:fit_test, mask: mask, user: managed_user)

        result = described_class.managed_by(manager_id: manager.id)

        expect(result.first['num_fit_tests_per_mask_user']).to eq(2)
      end

      it 'includes shipping status information' do
        result = described_class.managed_by(manager_id: manager.id)

        expect(result.first['mask_kit_uuid']).to eq(mask_kit_status.uuid)
      end
    end

    context 'when user is an admin' do
      before do
        manager.update!(admin: true)
      end

      it 'returns all masks regardless of manager' do
        other_mask = create(:mask)

        result = described_class.managed_by(manager_id: manager.id)

        expect(result.map { |r| r['id'] }).to include(mask.id, other_mask.id)
      end
    end

    context 'when mask has no fit tests' do
      it 'returns zero for fit test count' do
        result = described_class.managed_by(manager_id: manager.id)

        expect(result.first['num_fit_tests_per_mask_user']).to eq(0)
      end
    end

    context 'when mask has no shipping status' do
      let(:shipping_status) do
        nil
      end

      let(:shipping_status_join) do
        nil
      end

      it 'returns empty result' do
        result = described_class.managed_by(manager_id: manager.id)

        expect(result).to be_empty
      end
    end
  end
end
