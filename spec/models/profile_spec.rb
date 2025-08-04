# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Profile, type: :model do
  context 'when creating' do
    let(:user) do
      User.create(
        email: 'some@email.com',
        password: 'password'
      )
    end

    let(:profile) do
      described_class.create(
        user_id: user.id,
        measurement_system: 'metric'
      )
    end

    it 'has an external_api_token' do
      expect(profile.external_api_token).to be_present
    end
  end
end
