# frozen_string_literal: true

require 'rails_helper'

describe MaskPair do
  let(:author) { create(:user) }
  let(:mask_a) { create(:mask, author: author, unique_internal_model_code: 'MASK-A') }
  let(:mask_b) { create(:mask, author: author, unique_internal_model_code: 'MASK-B') }
  let(:mask_c) { create(:mask, author: author, unique_internal_model_code: 'MASK-C') }

  describe 'associations' do
    it 'belongs to mask_a' do
      pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])
      expect(pair.mask_a).to eq(mask_a)
    end

    it 'belongs to mask_b' do
      pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])
      expect(pair.mask_b).to eq(mask_b)
    end
  end

  describe 'validations' do
    describe 'name_distance' do
      it 'requires name_distance to be present' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: nil, history: [])
        expect(pair).not_to be_valid
        expect(pair.errors[:name_distance]).to include("can't be blank")
      end

      it 'allows valid name_distance' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])
        expect(pair).to be_valid
      end
    end

    describe 'history' do
      it 'must be an array' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: 'not an array')
        expect(pair).not_to be_valid
        expect(pair.errors[:history]).to include('must be an array')
      end

      it 'allows empty array' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])
        expect(pair).to be_valid
      end

      it 'allows array with valid history entries' do
        history = [
          {
            'author_id' => author.id,
            'duplicate' => false,
            'datetime' => '2025-01-01 01:01:00'
          },
          {
            'author_id' => author.id,
            'duplicate' => true,
            'datetime' => '2025-01-01 01:01:00'
          }
        ]
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: history)
        expect(pair).to be_valid
      end
    end

    describe 'uniqueness' do
      it 'prevents duplicate pairs with same order' do
        create(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])

        duplicate = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.6, history: [])
        expect(duplicate).not_to be_valid
        expect(duplicate.errors[:mask_a_id]).to include('pair already exists')
      end

      it 'prevents duplicate pairs with reversed order' do
        create(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])

        # Even if created with reversed order, it should be normalized and detected as duplicate
        duplicate = build(:mask_pair, mask_a: mask_b, mask_b: mask_a, name_distance: 0.6, history: [])
        duplicate.valid? # Trigger normalization
        expect(duplicate).not_to be_valid
        expect(duplicate.errors[:mask_a_id]).to include('pair already exists')
      end

      it 'allows different pairs' do
        create(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])

        different_pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_c, name_distance: 0.6, history: [])
        expect(different_pair).to be_valid
      end
    end

    describe 'self-reference prevention' do
      it 'prevents a mask from being paired with itself' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_a, name_distance: 0.5, history: [])
        expect(pair).not_to be_valid
        expect(pair.errors[:base]).to include('mask_a_id must be less than mask_b_id')
      end
    end

    describe 'mask_a_id_less_than_mask_b_id' do
      it 'requires mask_a_id to be less than mask_b_id' do
        pair = build(:mask_pair, mask_a: mask_b, mask_b: mask_a, name_distance: 0.5, history: [])
        # The normalize_pair_order callback should swap them, so validation should pass
        pair.valid?
        expect(pair.mask_a_id).to be < pair.mask_b_id
      end
    end
  end

  describe 'callbacks' do
    describe 'normalize_pair_order' do
      it 'swaps mask_a_id and mask_b_id if mask_a_id > mask_b_id' do
        # Ensure mask_b has a higher ID than mask_a for this test
        mask_with_lower_id = mask_a.id < mask_b.id ? mask_a : mask_b
        mask_with_higher_id = mask_a.id < mask_b.id ? mask_b : mask_a

        pair = build(:mask_pair, mask_a: mask_with_higher_id, mask_b: mask_with_lower_id, name_distance: 0.5, history: [])
        original_a_id = pair.mask_a_id
        original_b_id = pair.mask_b_id

        pair.valid? # Trigger callback

        expect(pair.mask_a_id).to eq(original_b_id)
        expect(pair.mask_b_id).to eq(original_a_id)
        expect(pair.mask_a_id).to be < pair.mask_b_id
      end

      it 'does not swap if mask_a_id < mask_b_id' do
        pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])
        original_a_id = pair.mask_a_id
        original_b_id = pair.mask_b_id

        pair.valid? # Trigger callback

        expect(pair.mask_a_id).to eq(original_a_id)
        expect(pair.mask_b_id).to eq(original_b_id)
      end

      it 'handles nil values gracefully' do
        pair = build(:mask_pair, mask_a: nil, mask_b: mask_b, name_distance: 0.5, history: [])
        expect { pair.valid? }.not_to raise_error
      end
    end
  end

  describe 'database constraints' do
    it 'enforces uniqueness at database level' do
      create(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])

      duplicate = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.6, history: [])
      expect { duplicate.save(validate: false) }.to raise_error(ActiveRecord::RecordNotUnique)
    end

    it 'enforces check constraint preventing self-reference' do
      pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_a, name_distance: 0.5, history: [])
      # Normalize will try to swap, but they're the same, so it won't help
      pair.mask_a_id = mask_a.id
      pair.mask_b_id = mask_a.id

      expect { pair.save(validate: false) }.to raise_error(ActiveRecord::StatementInvalid)
    end

    it 'enforces foreign key constraint with RESTRICT on delete' do
      pair = create(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: [])

      expect { mask_a.destroy }.to raise_error(ActiveRecord::DeleteRestrictionError)
    end
  end

  describe 'history structure' do
    it 'accepts history with valid structure' do
      history = [
        {
          'author_id' => author.id,
          'duplicate' => false,
          'datetime' => '2025-01-01 01:01:00'
        }
      ]
      pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: history)
      expect(pair).to be_valid
    end

    it 'allows history with multiple entries' do
      history = [
        {
          'author_id' => author.id,
          'duplicate' => false,
          'datetime' => '2025-01-01 01:01:00'
        },
        {
          'author_id' => author.id,
          'duplicate' => true,
          'datetime' => '2025-01-01 02:02:00'
        }
      ]
      pair = build(:mask_pair, mask_a: mask_a, mask_b: mask_b, name_distance: 0.5, history: history)
      expect(pair).to be_valid
      expect(pair.history.length).to eq(2)
    end
  end
end
