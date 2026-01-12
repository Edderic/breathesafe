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
  end
end
