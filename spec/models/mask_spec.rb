require 'rails_helper'

describe Mask do
  describe ".payable_on(date)" do
    subject do
      Mask.find_payable_on(date)
    end

    describe "when date 1 and date 2 are present" do
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

      describe "when date is before date 1" do
        let(:date) do
          2.weeks.ago
        end

        it "should be empty" do
          expect(subject).to be_empty
        end
      end

      describe "when date is after date 2" do
        let(:date) do
          2.weeks.from_now
        end

        it "should be empty" do
          expect(subject).to be_empty
        end
      end

      describe "when date is in between date 1 and 2" do
        let(:date) do
          4.days.ago
        end

        it "should be empty" do
          expect(subject).to include(mask)
        end
      end
    end

    describe "when date 1 is present but not date 2" do
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

      describe "when date is before date 1" do
        let(:date) do
          2.weeks.ago
        end

        it "should be empty" do
          expect(subject).to be_empty
        end
      end

      describe "when date is after date 1" do
        let(:date) do
          2.weeks.from_now
        end

        it "should be empty" do
          expect(subject).to include(mask)
        end
      end
    end
  end
end
