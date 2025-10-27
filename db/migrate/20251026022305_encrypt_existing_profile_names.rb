# frozen_string_literal: true

class EncryptExistingProfileNames < ActiveRecord::Migration[7.0]
  def up
    # This migration will encrypt existing first_name and last_name data
    # We need to temporarily disable encryption to read the plain text data
    # and then re-enable it to encrypt the data

    say 'Starting encryption of existing profile names...'

    # Temporarily disable encryption to read plain text data
    original_encryption_config = Rails.application.config.active_record.encryption
    Rails.application.config.active_record.encryption = nil

    # Get all profiles with non-nil names using raw SQL to avoid encryption
    profiles_to_encrypt = ActiveRecord::Base.connection.execute(
      <<-SQL
      SELECT id, first_name, last_name FROM profiles
      WHERE first_name IS NOT NULL AND first_name != ''
      OR last_name IS NOT NULL AND last_name != ''
      SQL
    )

    say "Found #{profiles_to_encrypt.count} profiles to encrypt"

    # Re-enable encryption
    Rails.application.config.active_record.encryption = original_encryption_config

    profiles_to_encrypt.each do |row|
      profile_id = row['id']
      plain_first_name = row['first_name']
      plain_last_name = row['last_name']

      # Update the profile with encrypted values
      # rubocop:disable Rails/SkipsModelValidations
      Profile.where(id: profile_id).update_all(
        first_name: plain_first_name,
        last_name: plain_last_name
      )
      # rubocop:enable Rails/SkipsModelValidations

      say "Encrypted profile #{profile_id}: #{plain_first_name} #{plain_last_name}"
    end

    say 'Completed encryption of existing profile names'
  end

  def down
    # This migration cannot be easily reversed because we can't decrypt
    # the data without the encryption keys. In a real scenario, you would
    # need to have a backup of the original data or implement a more
    # sophisticated rollback strategy.

    say 'WARNING: This migration cannot be reversed automatically.'
    say 'The encrypted data cannot be decrypted without the encryption keys.'
    say 'If you need to rollback, restore from a database backup taken before this migration.'

    raise ActiveRecord::IrreversibleMigration, 'Cannot reverse encryption migration'
  end
end
