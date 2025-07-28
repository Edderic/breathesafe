# frozen_string_literal: true

require 'rails_helper'

describe Mask do
  describe '.payable_on(date)' do
    subject do
      Mask.find_payable_on(date)
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
        Mask.create!(
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

        it 'should be empty' do
          expect(subject).to be_empty
        end
      end

      describe 'when date is after date 2' do
        let(:date) do
          2.weeks.from_now
        end

        it 'should be empty' do
          expect(subject).to be_empty
        end
      end

      describe 'when date is in between date 1 and 2' do
        let(:date) do
          4.days.ago
        end

        it 'should be empty' do
          expect(subject).to include(mask)
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
        Mask.create!(
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

        it 'should be empty' do
          expect(subject).to be_empty
        end
      end

      describe 'when date is after date 1' do
        let(:date) do
          2.weeks.from_now
        end

        it 'should be empty' do
          expect(subject).to include(mask)
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
      # Debug: Print the actual data in the database
      puts "\nDebug: Raw breathability data:"
      puts Mask.find(mask.id).breathability.inspect

      result = described_class.with_privacy_aggregations([mask.id])

      # Debug: Print the result
      puts "\nDebug: Result data:"
      puts result.first.inspect

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
end
