require 'rails_helper'

RSpec.describe User, type: :model do
  context "on create" do

    let(:user) do
      User.create(
        email: 'some@email.com',
        password: 'password'
      )
    end

    it "should have an external_api_token " do
      user
      expect(User.find_by(email: 'some@email.com').external_api_token).to be_present

    end
  end
end
