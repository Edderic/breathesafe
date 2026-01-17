# frozen_string_literal: true

class AddFormsToUsers < ActiveRecord::Migration[7.0]
  def up
    # Add the forms jsonb column with a default empty hash
    add_column :users, :forms, :jsonb, default: {}, null: false

    # Migrate existing consent_form data into the new forms structure
    say_with_time 'Migrating existing consent form data to forms jsonb field' do
      migration_user = Class.new(ActiveRecord::Base) do
        self.table_name = 'users'
      end

      migration_user.find_each do |user|
        forms_data = {}

        # Migrate consent_form data if it exists
        # Convert old date format to UTC timestamp format for consistency
        if user.consent_form_version_accepted.present?
          # Try to parse the old version and convert to UTC timestamp
          # Old format might be "2025-12-13" or "2025-10-25"
          old_version = user.consent_form_version_accepted
          begin
            # Parse as date and convert to UTC timestamp
            date = Date.parse(old_version)
            utc_version = "#{date.iso8601}T00:00:00Z"
          rescue ArgumentError
            # If parsing fails, use as-is
            utc_version = old_version
          end

          forms_data['consent_form'] = {
            'version_accepted' => utc_version,
            'accepted_at' => user.consent_form_accepted_at&.utc&.iso8601
          }
        else
          forms_data['consent_form'] = { 'version_accepted' => nil, 'accepted_at' => nil }
        end

        # Initialize other forms as not accepted
        forms_data['disclaimer'] = { 'version_accepted' => nil, 'accepted_at' => nil }
        forms_data['terms_of_service'] = { 'version_accepted' => nil, 'accepted_at' => nil }
        forms_data['privacy_policy'] = { 'version_accepted' => nil, 'accepted_at' => nil }

        user.update_column(:forms, forms_data)
      end
    end
  end

  def down
    remove_column :users, :forms
  end
end
