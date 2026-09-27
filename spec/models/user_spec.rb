# frozen_string_literal: true

require 'rails_helper'

RSpec.describe User, type: :model do
  describe '#soft_delete!' do
    it 'anonymizes the account and deletes user-owned personal data' do
      user = create(:user, :with_profile)
      facial_measurement = create(:facial_measurement, user: user)
      measurement_device = create(:measurement_device, owner: user)
      authored_mask = create(:mask, author: user)

      Address.create!(user_id: user.id)
      UserCarbonDioxideMonitor.create!(user: user, serial: 'co2-1', model: 'aranet')
      BulkFitTestsImport.create!(user: user, source_name: 'admin import', source_type: 'csv')
      target_fit_test = create(
        :fit_test,
        user: user,
        facial_measurement: facial_measurement,
        quantitative_fit_testing_device: measurement_device
      )

      survivor = create(:user)
      surviving_fit_test = create(
        :fit_test,
        user: survivor,
        source_fit_test: target_fit_test,
        quantitative_fit_testing_device: measurement_device
      )

      user.soft_delete!

      deleted_user = described_class.with_deleted.find(user.id)
      expect(deleted_user).to be_deleted
      expect(deleted_user.email).to match(/\Adeleted_user_[\w-]+@example\.invalid\z/)
      expect(deleted_user.unconfirmed_email).to be_nil

      expect(Profile.where(user_id: user.id)).to be_empty
      expect(FacialMeasurement.where(user_id: user.id)).to be_empty
      expect(FitTest.where(user_id: user.id)).to be_empty
      expect(Address.where(user_id: user.id)).to be_empty
      expect(UserCarbonDioxideMonitor.where(user_id: user.id)).to be_empty
      expect(BulkFitTestsImport.where(user_id: user.id)).to be_empty
      expect(MeasurementDevice.where(owner_id: user.id)).to be_empty
      expect(Mask.exists?(authored_mask.id)).to be(true)

      expect(surviving_fit_test.reload.source_fit_test_id).to be_nil
      expect(surviving_fit_test.quantitative_fit_testing_device_id).to be_nil
    end

    it 'deletes managed users personal data using existing manager behavior' do
      manager = create(:user)
      managed = create(:user, :with_profile)
      ManagedUser.create!(manager: manager, managed: managed)

      manager.soft_delete!

      expect(Profile.where(user_id: managed.id)).to be_empty
      expect(ManagedUser.where(manager_id: manager.id)).to be_empty
      expect(ManagedUser.where(managed_id: managed.id)).to be_empty
    end
  end
end
