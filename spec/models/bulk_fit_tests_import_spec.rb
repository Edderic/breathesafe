# frozen_string_literal: true

require 'rails_helper'

RSpec.describe BulkFitTestsImport, type: :model do
  let(:user) do
    User.create(
      email: 'test@example.com',
      password: 'password123',
      confirmed_at: Time.current
    )
  end

  let(:valid_attributes) do
    {
      user: user,
      source_name: 'test_file.csv',
      source_type: 'CSV',
      status: 'pending',
      column_matching_mapping: {},
      user_matching: '{}',
      mask_matching: {},
      user_seal_check_matching: {},
      fit_testing_matching: {}
    }
  end

  describe 'validations' do
    context 'when source_name is missing' do
      it 'is invalid' do
        import = described_class.new(valid_attributes.except(:source_name))
        expect(import).not_to be_valid
        expect(import.errors[:source_name]).to include("can't be blank")
      end
    end

    context 'when source_type is missing' do
      it 'is invalid' do
        import = described_class.new(valid_attributes.except(:source_type))
        expect(import).not_to be_valid
        expect(import.errors[:source_type]).to include("can't be blank")
      end
    end

    context 'when status is invalid' do
      it 'is invalid' do
        import = described_class.new(valid_attributes.merge(status: 'invalid_status'))
        expect(import).not_to be_valid
        expect(import.errors[:status]).to be_present
      end
    end

    context 'when status is valid' do
      %w[pending processing completed failed].each do |status|
        it "accepts #{status}" do
          import = described_class.new(valid_attributes.merge(status: status))
          expect(import).to be_valid
        end
      end
    end
  end

  describe 'import_data CSV validation' do
    context 'when import_data is blank' do
      it 'is valid' do
        import = described_class.new(valid_attributes)
        expect(import).to be_valid
      end
    end

    context 'when import_data is valid CSV' do
      let(:valid_csv) do
        <<~CSV
          Name,Email,Age
          John Doe,john@example.com,30
          Jane Smith,jane@example.com,25
        CSV
      end

      it 'is valid' do
        import = described_class.new(valid_attributes.merge(import_data: valid_csv))
        expect(import).to be_valid
      end
    end

    context 'when import_data is valid CSV with quoted fields' do
      let(:valid_csv_with_quotes) do
        <<~CSV
          Name,Email,Description
          John Doe,john@example.com,"John, the developer"
          Jane Smith,jane@example.com,"Jane, the designer"
        CSV
      end

      it 'is valid' do
        import = described_class.new(valid_attributes.merge(import_data: valid_csv_with_quotes))
        expect(import).to be_valid
      end
    end

    context 'when import_data is valid CSV with empty lines' do
      let(:valid_csv_with_empty_lines) do
        <<~CSV
          Name,Email,Age
          John Doe,john@example.com,30

          Jane Smith,jane@example.com,25
        CSV
      end

      it 'is valid' do
        import = described_class.new(valid_attributes.merge(import_data: valid_csv_with_empty_lines))
        expect(import).to be_valid
      end
    end

    context 'when import_data is invalid CSV' do
      let(:invalid_csv) do
        <<~CSV
          Name,Email,Age
          John Doe,john@example.com,30
          Jane Smith,"unclosed quote,jane@example.com,25
        CSV
      end

      it 'is invalid' do
        import = described_class.new(valid_attributes.merge(import_data: invalid_csv))
        expect(import).not_to be_valid
        expect(import.errors[:import_data]).to be_present
      end
    end

    context 'when import_data is not CSV at all' do
      let(:not_csv) do
        <<~TEXT
          This is just plain text
          Not CSV format at all
        TEXT
      end

      it 'is valid (plain text can be parsed as CSV with single column)' do
        import = described_class.new(valid_attributes.merge(import_data: not_csv))
        # Plain text can technically be parsed as CSV (each line becomes a row with one column)
        expect(import).to be_valid
      end
    end

    context 'when import_data has malformed CSV structure' do
      let(:malformed_csv) do
        <<~CSV
          Name,Email,Age
          John Doe,john@example.com,30,extra,columns
          Jane Smith,jane@example.com
        CSV
      end

      it 'is valid (CSV parser accepts varying column counts)' do
        import = described_class.new(valid_attributes.merge(import_data: malformed_csv))
        # CSV parser accepts varying column counts, so this is technically valid CSV
        expect(import).to be_valid
      end
    end
  end

  describe 'encryption' do
    context 'when saving import_data' do
      let(:csv_data) do
        <<~CSV
          Name,Email,Age
          John Doe,john@example.com,30
        CSV
      end

      it 'saves and retrieves import_data correctly' do
        import = described_class.create!(valid_attributes.merge(import_data: csv_data))

        # Reload from database
        import.reload

        # When accessed through the model, it should be decrypted correctly
        expect(import.import_data).to eq(csv_data)
      end

      it 'persists import_data across database operations' do
        import = described_class.create!(valid_attributes.merge(import_data: csv_data))
        import_id = import.id

        # Find the record again
        found_import = described_class.find(import_id)

        expect(found_import.import_data).to eq(csv_data)
      end
    end

    context 'when saving user_matching' do
      let(:user_matching_data) { '{"user1": "email1@example.com", "user2": "email2@example.com"}' }

      it 'saves and retrieves user_matching correctly' do
        import = described_class.create!(valid_attributes.merge(user_matching: user_matching_data))

        # Reload from database
        import.reload

        # When accessed through the model, it should be decrypted correctly
        expect(import.user_matching).to eq(user_matching_data)
      end

      it 'persists user_matching across database operations' do
        import = described_class.create!(valid_attributes.merge(user_matching: user_matching_data))
        import_id = import.id

        # Find the record again
        found_import = described_class.find(import_id)

        expect(found_import.user_matching).to eq(user_matching_data)
      end
    end
  end

  describe 'associations' do
    it 'belongs to user' do
      import = described_class.new(valid_attributes)
      expect(import.user).to eq(user)
    end

    it 'has many masks' do
      import = described_class.create!(valid_attributes)
      mask = Mask.create!(
        unique_internal_model_code: 'TEST-MASK-001',
        author: user,
        bulk_fit_tests_import: import
      )

      expect(import.masks).to include(mask)
    end

    it 'has many fit_tests' do
      import = described_class.create!(valid_attributes)
      fit_test = FitTest.create!(
        user: user,
        bulk_fit_tests_import: import
      )

      expect(import.fit_tests).to include(fit_test)
    end

    context 'when bulk_fit_tests_import is destroyed' do
      it 'destroys associated masks' do
        import = described_class.create!(valid_attributes)
        mask = Mask.create!(
          unique_internal_model_code: 'TEST-MASK-001',
          author: user,
          bulk_fit_tests_import: import
        )

        import.destroy

        expect(Mask.find_by(id: mask.id)).to be_nil
      end

      it 'destroys associated fit_tests' do
        import = described_class.create!(valid_attributes)
        fit_test = FitTest.create!(
          user: user,
          bulk_fit_tests_import: import
        )

        import.destroy

        expect(FitTest.find_by(id: fit_test.id)).to be_nil
      end
    end
  end
end
