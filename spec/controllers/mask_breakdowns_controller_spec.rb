# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskBreakdownsController, type: :controller do
  let(:admin) { create(:user, :admin) }
  let(:author) { create(:user) }

  before do
    allow(controller).to receive(:authenticate_user!).and_return(true)
    allow(controller).to receive(:current_user).and_return(admin)
  end

  describe 'GET #index' do
    it 'treats requires_review breakdowns as incomplete' do
      review_mask = create(:mask, author: author, unique_internal_model_code: '3M Aura 9205+ N95')
      complete_mask = create(:mask, author: author, unique_internal_model_code: 'Honeywell H910 KN95')

      MaskEvent.create!(
        mask: review_mask,
        user: admin,
        event_type: 'breakdown_updated',
        data: {
          'breakdown' => [{ '3M' => 'brand' }, { 'Aura' => 'model' }, { 'N95' => 'filter_type' }],
          'requires_review' => true
        }
      )

      MaskEvent.create!(
        mask: complete_mask,
        user: admin,
        event_type: 'breakdown_updated',
        data: {
          'breakdown' => [{ 'Honeywell' => 'brand' }, { 'H910' => 'model' }, { 'KN95' => 'filter_type' }],
          'requires_review' => false
        }
      )

      get :index, params: { filter: 'complete' }, as: :json

      expect(response).to have_http_status(:ok)

      body = JSON.parse(response.body)
      ids = body['masks'].map { |row| row['id'] }

      expect(ids).to include(complete_mask.id)
      expect(ids).not_to include(review_mask.id)
      expect(body['completed_count']).to eq(1)
    end
  end

  describe 'GET #show' do
    it 'returns review-required breakdown as incomplete' do
      mask = create(:mask, author: author, unique_internal_model_code: '3M Aura 9205+ N95')

      MaskEvent.create!(
        mask: mask,
        user: admin,
        event_type: 'breakdown_updated',
        data: {
          'breakdown' => [{ '3M' => 'brand' }, { 'Aura' => 'model' }, { 'N95' => 'filter_type' }],
          'requires_review' => true
        }
      )

      get :show, params: { id: mask.id }, as: :json

      expect(response).to have_http_status(:ok)

      body = JSON.parse(response.body)
      expect(body['breakdown_requires_review']).to eq(true)
      expect(body['breakdown_complete']).to eq(false)
    end
  end

  describe 'POST #create' do
    it 'clears requires_review for manual edits' do
      mask = create(:mask, author: author, unique_internal_model_code: '3M Aura 9205+ N95')
      breakdown = [{ '3M' => 'brand' }, { 'Aura' => 'model' }, { 'N95' => 'filter_type' }]

      expect do
        post :create, params: { mask_id: mask.id, breakdown: breakdown }, as: :json
      end.to change(MaskEvent, :count).by(1)

      expect(response).to have_http_status(:created)

      created_event = MaskEvent.order(:created_at).last
      body = JSON.parse(response.body)

      expect(created_event.data['requires_review']).to eq(false)
      expect(created_event.data['source']).to eq('manual')
      expect(body.dig('breakdown', 'requires_review')).to eq(false)
      expect(body.dig('breakdown', 'complete')).to eq(true)
    end
  end
end
