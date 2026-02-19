# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskDuplicateChainFlattener do
  let(:author) { create(:user) }
  let(:admin) { create(:user, :admin) }

  describe '.call' do
    it 'produces a flatten plan in dry-run mode for chain links' do
      root = create(:mask, author: author, unique_internal_model_code: 'ROOT')
      child = create(:mask, author: author, unique_internal_model_code: 'CHILD', duplicate_of: root.id)
      grandchild = create(:mask, author: author, unique_internal_model_code: 'GRANDCHILD', duplicate_of: child.id)

      result = described_class.call

      expect(result[:apply]).to eq(false)
      expect(result[:total_duplicates]).to eq(2)
      expect(result[:flatten_candidates]).to eq(1)
      expect(result[:planned]).to include(
        hash_including(
          mask_id: grandchild.id,
          current_duplicate_of: child.id,
          canonical_root_id: root.id
        )
      )
    end

    it 'applies flatten plan and emits duplicate_marked events' do
      root = create(:mask, author: author, unique_internal_model_code: 'ROOT')
      child = create(:mask, author: author, unique_internal_model_code: 'CHILD', duplicate_of: root.id)
      grandchild = create(:mask, author: author, unique_internal_model_code: 'GRANDCHILD', duplicate_of: child.id)

      expect do
        result = described_class.call(apply: true, user: admin)
        expect(result[:errors]).to be_empty
        expect(result[:changed].map { |entry| entry[:mask_id] }).to include(grandchild.id)
      end.to change(MaskEvent, :count).by(1)

      expect(grandchild.reload.duplicate_of).to eq(root.id)
    end

    it 'raises when apply=true without user' do
      create(:mask, author: author, unique_internal_model_code: 'ROOT')
      expect { described_class.call(apply: true) }.to raise_error(MaskDuplicateChainFlattener::Error)
    end
  end
end
