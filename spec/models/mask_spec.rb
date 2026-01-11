# frozen_string_literal: true

require 'rails_helper'

describe Mask do
  describe '.payable_on(date)' do
    subject(:payable_date_on) do
      described_class.find_payable_on(date)
    end

    describe 'when date 1 and date 2 are present' do
      let(:date_1) do
        DateTime.now - 1.week
      end

      let(:date_2) do
        DateTime.now - 3.days
      end

      let(:user) do
        User.create(
          email: 'e@s.com',
          password: 'helloworld'
        )
      end

      let!(:mask) do
        described_class.create!(
          unique_internal_model_code: 'abc',
          author_id: user.id,
          payable_datetimes: [
            {
              start_datetime: date_1,
              end_datetime: date_2
            }
          ]
        )
      end

      describe 'when date is before date 1' do
        let(:date) do
          2.weeks.ago
        end

        it 'is empty' do
          expect(payable_date_on).to be_empty
        end
      end

      describe 'when date is after date 2' do
        let(:date) do
          2.weeks.from_now
        end

        it 'is empty' do
          expect(payable_date_on).to be_empty
        end
      end

      describe 'when date is in between date 1 and 2' do
        let(:date) do
          4.days.ago
        end

        it 'is empty' do
          expect(payable_date_on).to include(mask)
        end
      end
    end

    describe 'when date 1 is present but not date 2' do
      let(:date_1) do
        DateTime.now - 1.week
      end

      let(:date_2) do
        nil
      end

      let(:user) do
        User.create(
          email: 'e@s.com',
          password: 'helloworld'
        )
      end

      let!(:mask) do
        described_class.create!(
          unique_internal_model_code: 'abc',
          author_id: user.id,
          payable_datetimes: [
            {
              start_datetime: date_1,
              end_datetime: date_2
            }
          ]
        )
      end

      describe 'when date is before date 1' do
        let(:date) do
          2.weeks.ago
        end

        it 'is empty' do
          expect(payable_date_on).to be_empty
        end
      end

      describe 'when date is after date 1' do
        let(:date) do
          2.weeks.from_now
        end

        it 'is empty' do
          expect(payable_date_on).to include(mask)
        end
      end
    end
  end

  describe '.with_privacy_aggregations' do
    let(:author) { create(:user) }
    let(:mask) do
      create(:mask,
             author: author,
             breathability: [
               {
                 breathability_pascals: 100,
                 breathability_pascals_notes: nil,
                 breathability_pascals_source: nil
               },
               {
                 breathability_pascals: 200,
                 breathability_pascals_notes: nil,
                 breathability_pascals_source: nil
               }
             ])
    end

    let(:mask_with_no_breathability) do
      create(:mask,
             author: author,
             breathability: [])
    end

    let(:mask_with_single_breathability) do
      create(:mask,
             author: author,
             breathability: [
               {
                 breathability_pascals: 150,
                 breathability_pascals_notes: nil,
                 breathability_pascals_source: nil
               }
             ])
    end

    before do
      mask
      mask_with_no_breathability
      mask_with_single_breathability
    end

    it 'calculates average breathability for masks with multiple measurements' do
      result = described_class.with_privacy_aggregations([mask.id])

      expect(result.first['avg_breathability_pa']).to eq(150.0) # (100 + 200) / 2
      expect(result.first['count_breathability']).to eq(2)
    end

    it 'returns nil for average breathability when mask has no measurements' do
      result = described_class.with_privacy_aggregations([mask_with_no_breathability.id])
      expect(result.first['avg_breathability_pa']).to be_nil
      expect(result.first['count_breathability']).to be_nil
    end

    it 'returns single value for average breathability when mask has one measurement' do
      result = described_class.with_privacy_aggregations([mask_with_single_breathability.id])
      expect(result.first['avg_breathability_pa']).to eq(150.0)
      expect(result.first['count_breathability']).to eq(1)
    end

    it 'calculates average breathability for all masks when no mask_ids provided' do
      result = described_class.with_privacy_aggregations
      masks_with_breathability = result.select { |m| m['avg_breathability_pa'].present? }

      expect(masks_with_breathability.length).to eq(2) # mask and mask_with_single_breathability
      expect(masks_with_breathability.map { |m| m['avg_breathability_pa'] }).to contain_exactly(150.0, 150.0)
    end

    it 'handles non-numeric breathability values gracefully' do
      mask_with_invalid_data = create(:mask,
                                      author: author,
                                      breathability: [
                                        {
                                          breathability_pascals: 'invalid',
                                          breathability_pascals_notes: nil,
                                          breathability_pascals_source: nil
                                        }
                                      ])

      result = described_class.with_privacy_aggregations([mask_with_invalid_data.id])
      expect(result.first['avg_breathability_pa']).to be_nil
    end
  end

  describe '.with_admin_aggregations' do
    let(:author) { create(:user) }
    let(:mask) do
      create(:mask,
             author: author,
             breathability: [
               {
                 breathability_pascals: 100,
                 breathability_pascals_notes: nil,
                 breathability_pascals_source: nil
               },
               {
                 breathability_pascals: 200,
                 breathability_pascals_notes: nil,
                 breathability_pascals_source: nil
               }
             ])
    end

    it 'preserves aggregated fields when merging admin demographics' do
      result = described_class.with_admin_aggregations([mask.id])

      expect(result.first['avg_breathability_pa']).to eq(150.0)
      expect(result.first['count_breathability']).to eq(2)
    end
  end

  describe 'duplicate_of validations' do
    let(:author) { create(:user) }
    let(:mask_a) { create(:mask, author: author, unique_internal_model_code: 'MASK-A') }
    let(:mask_b) { create(:mask, author: author, unique_internal_model_code: 'MASK-B') }
    let(:mask_c) { create(:mask, author: author, unique_internal_model_code: 'MASK-C') }

    describe 'cannot_be_duplicate_of_self' do
      it 'prevents a mask from being a duplicate of itself' do
        mask_a.duplicate_of = mask_a.id
        expect(mask_a).not_to be_valid
        expect(mask_a.errors[:duplicate_of]).to include('cannot reference itself')
      end

      it 'allows nil duplicate_of' do
        mask_a.duplicate_of = nil
        expect(mask_a).to be_valid
      end

      it 'allows a mask to reference a different mask' do
        mask_a.duplicate_of = mask_b.id
        expect(mask_a).to be_valid
      end
    end

    describe 'cannot_create_circular_reference' do
      context 'when creating a simple circular reference (A -> B -> A)' do
        before do
          mask_b.duplicate_of = mask_a.id
          mask_b.save!
        end

        it 'prevents mask A from referencing mask B' do
          mask_a.duplicate_of = mask_b.id
          expect(mask_a).not_to be_valid
          expect(mask_a.errors[:duplicate_of]).to include('would create a circular reference')
        end
      end

      context 'when creating a longer circular reference (A -> B -> C -> A)' do
        before do
          mask_b.duplicate_of = mask_a.id
          mask_b.save!
          mask_c.duplicate_of = mask_b.id
          mask_c.save!
        end

        it 'prevents mask A from referencing mask C' do
          mask_a.duplicate_of = mask_c.id
          expect(mask_a).not_to be_valid
          expect(mask_a.errors[:duplicate_of]).to include('would create a circular reference')
        end
      end

      context 'when creating a valid chain (A -> B -> C)' do
        before do
          mask_b.duplicate_of = mask_a.id
          mask_b.save!
          mask_c.duplicate_of = mask_b.id
          mask_c.save!
        end

        it 'allows the chain to exist' do
          expect(mask_b.reload.duplicate_of).to eq(mask_a.id)
          expect(mask_c.reload.duplicate_of).to eq(mask_b.id)
        end

        it 'allows a new mask to reference mask C' do
          mask_d = build(:mask, author: author, unique_internal_model_code: 'MASK-D')
          mask_d.duplicate_of = mask_c.id
          expect(mask_d).to be_valid
        end
      end

      context 'when multiple masks reference the same duplicate_of' do
        before do
          mask_b.duplicate_of = mask_a.id
          mask_b.save!
        end

        it 'allows multiple masks to reference the same parent' do
          mask_c.duplicate_of = mask_a.id
          expect(mask_c).to be_valid
          mask_c.save!

          expect(mask_b.reload.duplicate_of).to eq(mask_a.id)
          expect(mask_c.reload.duplicate_of).to eq(mask_a.id)
        end
      end

      context 'when updating an existing duplicate_of' do
        before do
          mask_b.duplicate_of = mask_a.id
          mask_b.save!
          mask_c.duplicate_of = mask_b.id
          mask_c.save!
        end

        it 'prevents updating to create a circular reference' do
          mask_a.duplicate_of = mask_c.id
          expect(mask_a).not_to be_valid
          expect(mask_a.errors[:duplicate_of]).to include('would create a circular reference')
        end

        it 'allows updating to a different valid mask' do
          mask_d = create(:mask, author: author, unique_internal_model_code: 'MASK-D')
          mask_a.duplicate_of = mask_d.id
          expect(mask_a).to be_valid
        end
      end

      context 'when the referenced mask does not exist' do
        it 'does not raise an error during validation' do
          mask_a.duplicate_of = 999_999
          # Validation should not crash, but the foreign key constraint will fail on save
          expect { mask_a.valid? }.not_to raise_error
        end
      end

      context 'when duplicate_of is nil' do
        it 'does not check for circular references' do
          mask_a.duplicate_of = nil
          expect(mask_a).to be_valid
        end
      end
    end
  end
end
