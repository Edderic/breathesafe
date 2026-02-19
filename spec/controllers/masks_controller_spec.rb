# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MasksController, type: :controller do
  let(:author) { create(:user) }
  let(:mask) { create(:mask, author: author, perimeter_mm: 300, strap_type: 'Headstrap', style: 'Cup') }

  before do
    allow(controller).to receive(:current_user).and_return(author)
  end

  describe 'PUT #update' do
    it 'emits mask events and updates the materialized mask state' do
      params = {
        id: mask.id,
        mask: {
          perimeter_mm: 320,
          strap_type: 'Earloop',
          style: 'Bifold',
          image_urls: ['https://example.com/new.png']
        }
      }

      expect do
        put :update, params: params, as: :json
      end.to change(MaskEvent, :count).by(4)

      expect(response).to have_http_status(:no_content)

      event_types = MaskEvent.where(mask_id: mask.id).pluck(:event_type)
      expect(event_types).to include('perimeter_updated', 'strap_type_updated', 'style_updated', 'image_urls_updated')

      mask.reload
      expect(mask.perimeter_mm).to eq(320)
      expect(mask.strap_type).to eq('Earloop')
      expect(mask.style).to eq('Bifold')
      expect(mask.image_urls).to eq(['https://example.com/new.png'])
    end

    it 'emits availability_updated when available changes' do
      params = {
        id: mask.id,
        mask: {
          available: false
        }
      }

      expect do
        put :update, params: params, as: :json
      end.to change(MaskEvent, :count).by(1)

      expect(response).to have_http_status(:no_content)
      event = MaskEvent.where(mask_id: mask.id).order(:created_at).last
      expect(event.event_type).to eq('availability_updated')

      mask.reload
      expect(mask.available).to eq(false)
    end

    it 'emits CRF-predicted breakdown_updated requiring review when unique_internal_model_code changes' do
      predicted_breakdown = [
        { '3M' => 'brand' },
        { 'Aura' => 'model' },
        { 'N95' => 'filter_type' }
      ]

      allow(MaskComponentPredictorService).to receive(:predict).with('3M Aura N95').and_return(
        {
          breakdown: predicted_breakdown,
          confidence: 0.93,
          fallback: false
        }
      )

      params = {
        id: mask.id,
        mask: {
          unique_internal_model_code: '3M Aura N95'
        }
      }

      expect do
        put :update, params: params, as: :json
      end.to change(MaskEvent, :count).by(2)

      expect(response).to have_http_status(:no_content)
      expect(MaskComponentPredictorService).to have_received(:predict).with('3M Aura N95')

      latest_events = MaskEvent.where(mask_id: mask.id).order(created_at: :desc).limit(2)
      unique_code_event = latest_events.find { |event| event.event_type == 'unique_internal_model_code_updated' }
      breakdown_event = latest_events.find { |event| event.event_type == 'breakdown_updated' }

      expect(unique_code_event).to be_present
      expect(breakdown_event).to be_present
      expect(breakdown_event.data['breakdown']).to eq(predicted_breakdown)
      expect(breakdown_event.data['requires_review']).to eq(true)
      expect(breakdown_event.data['source']).to eq('crf_auto_rename')
      expect(breakdown_event.data['confidence']).to eq(0.93)
      expect(breakdown_event.notes).to include('Auto-generated from CRF')

      mask.reload
      expect(mask.unique_internal_model_code).to eq('3M Aura N95')
      expect(mask.current_state['breakdown']).to eq(predicted_breakdown)
    end
  end

  describe 'GET #index' do
    let!(:available_mask) do
      create(:mask, author: author, available: true, unique_internal_model_code: 'AVAILABLE-MASK')
    end
    let!(:unavailable_mask) do
      create(:mask, author: author, available: false, unique_internal_model_code: 'UNAVAILABLE-MASK')
    end

    it 'defaults to available-only masks' do
      get :index, params: {}, as: :json

      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      ids = body['masks'].map { |m| m['id'] }
      expect(ids).to include(available_mask.id)
      expect(ids).not_to include(unavailable_mask.id)
    end

    it 'includes unavailable masks when filter_available=false' do
      get :index, params: { filter_available: 'false' }, as: :json

      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      ids = body['masks'].map { |m| m['id'] }
      expect(ids).to include(available_mask.id)
      expect(ids).to include(unavailable_mask.id)
    end
  end
end
