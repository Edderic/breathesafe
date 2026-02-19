# frozen_string_literal: true

require 'rails_helper'

RSpec.describe Admin::MaskDuplicatesController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:admin) { create(:user, :admin) }
  let(:non_admin) { create(:user) }
  let(:author) { create(:user) }

  describe 'POST #create' do
    let(:root_mask) { create(:mask, author: author, unique_internal_model_code: 'ROOT-MASK') }
    let(:intermediate_mask) do
      create(:mask, author: author, unique_internal_model_code: 'INTERMEDIATE-MASK', duplicate_of: root_mask.id)
    end
    let(:child_mask) { create(:mask, author: author, unique_internal_model_code: 'CHILD-MASK') }

    context 'when admin' do
      before { sign_in admin }

      it 'links child to canonical root when target is not a root' do
        expect do
          post :create, params: { mask_id: child_mask.id, target_mask_id: intermediate_mask.id }, format: :json
        end.to change(MaskEvent, :count).by(1)

        expect(response).to have_http_status(:ok)

        child_mask.reload
        expect(child_mask.duplicate_of).to eq(root_mask.id)

        event = MaskEvent.order(:created_at).last
        expect(event.event_type).to eq('duplicate_marked')
        expect(event.data['duplicate_of']).to eq(root_mask.id)

        body = JSON.parse(response.body)
        expect(body.dig('duplicate_link', 'canonical_target_mask_id')).to eq(root_mask.id)
        expect(body.dig('duplicate_link', 'changed')).to eq(true)
      end

      it 'returns validation error when linking a mask to itself' do
        post :create, params: { mask_id: root_mask.id, target_mask_id: root_mask.id }, format: :json

        expect(response).to have_http_status(:unprocessable_entity)
        expect(JSON.parse(response.body)['error']).to include('cannot be marked as a duplicate of itself')
      end

      it 'returns unprocessable entity when target_mask_id is missing' do
        post :create, params: { mask_id: child_mask.id }, format: :json

        expect(response).to have_http_status(:unprocessable_entity)
        expect(JSON.parse(response.body)['error']).to include('target_mask_id is required')
      end
    end

    context 'when non-admin' do
      before { sign_in non_admin }

      it 'returns forbidden' do
        post :create, params: { mask_id: child_mask.id, target_mask_id: root_mask.id }, format: :json
        expect(response).to have_http_status(:forbidden)
      end
    end
  end

  describe 'DELETE #destroy' do
    let(:root_mask) { create(:mask, author: author, unique_internal_model_code: 'ROOT-MASK') }
    let(:child_mask) do
      create(:mask, author: author, unique_internal_model_code: 'CHILD-MASK', duplicate_of: root_mask.id)
    end

    before { sign_in admin }

    it 'unlinks duplicate and emits duplicate_marked event with nil duplicate_of' do
      expect do
        delete :destroy, params: { mask_id: child_mask.id }, format: :json
      end.to change(MaskEvent, :count).by(1)

      expect(response).to have_http_status(:ok)

      child_mask.reload
      expect(child_mask.duplicate_of).to be_nil

      event = MaskEvent.order(:created_at).last
      expect(event.event_type).to eq('duplicate_marked')
      expect(event.data['duplicate_of']).to be_nil

      body = JSON.parse(response.body)
      expect(body.dig('duplicate_link', 'changed')).to eq(true)
      expect(body.dig('duplicate_link', 'duplicate_of')).to be_nil
    end
  end
end
