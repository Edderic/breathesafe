# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Admin::MaskFitFamiliesController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:admin) { create(:user, :admin) }
  let(:author) { create(:user) }
  let(:fit_family) { create(:fit_family) }
  let(:target_fit_family) { create(:fit_family) }
  let(:mask) { create(:mask, author: author, fit_family: fit_family) }

  before { sign_in admin }

  describe 'PUT #update' do
    it 'assigns the mask to a different fit family' do
      put :update, params: {
        mask_id: mask.id,
        mask_fit_family: {
          fit_family_id: target_fit_family.id
        }
      }, format: :json

      expect(response).to have_http_status(:ok)
      expect(mask.reload.fit_family_id).to eq(target_fit_family.id)
    end
  end
end
