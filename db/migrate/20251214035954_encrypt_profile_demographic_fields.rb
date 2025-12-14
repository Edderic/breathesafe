# frozen_string_literal: true

class EncryptProfileDemographicFields < ActiveRecord::Migration[7.0]
  def up
    # First, change year_of_birth from integer to text to support encryption
    say_with_time 'Converting year_of_birth column to text' do
      # Create a temporary column to store the integer values
      add_column :profiles, :year_of_birth_temp, :text

      # Copy integer values to temp column as text
      execute 'UPDATE profiles SET year_of_birth_temp = year_of_birth::text WHERE year_of_birth IS NOT NULL'

      # Drop the old integer column and rename temp column
      remove_column :profiles, :year_of_birth
      rename_column :profiles, :year_of_birth_temp, :year_of_birth
    end

    # Enable support for reading unencrypted data during migration
    ActiveRecord::Encryption.config.support_unencrypted_data = true

    say_with_time "Encrypting demographic fields for #{Profile.count} profiles" do
      # Reload the Profile model to pick up the new column type
      Profile.reset_column_information

      # Get encryption types for each field
      race_ethnicity_type = Profile.type_for_attribute(:race_ethnicity)
      gender_and_sex_type = Profile.type_for_attribute(:gender_and_sex)
      other_gender_type = Profile.type_for_attribute(:other_gender)
      year_of_birth_type = Profile.type_for_attribute(:year_of_birth)

      Profile.find_each do |profile|
        # Read unencrypted values
        race_eth = profile.race_ethnicity
        gender_sex = profile.gender_and_sex
        other_gen = profile.other_gender
        year_birth = profile.year_of_birth

        # Only update if there's demographic data to encrypt
        has_data = race_eth.present? || gender_sex.present? || other_gen.present? || year_birth.present?

        if has_data
          # Manually encrypt each value using the type serializer
          encrypted_race = race_eth.present? ? race_ethnicity_type.serialize(race_eth) : nil
          encrypted_gender = gender_sex.present? ? gender_and_sex_type.serialize(gender_sex) : nil
          encrypted_other = other_gen.present? ? other_gender_type.serialize(other_gen) : nil
          encrypted_year = year_birth.present? ? year_of_birth_type.serialize(year_birth) : nil

          # Update directly in database with encrypted values
          update_sql = []
          update_sql << "race_ethnicity = #{connection.quote(encrypted_race)}" if encrypted_race
          update_sql << "gender_and_sex = #{connection.quote(encrypted_gender)}" if encrypted_gender
          update_sql << "other_gender = #{connection.quote(encrypted_other)}" if encrypted_other
          update_sql << "year_of_birth = #{connection.quote(encrypted_year)}" if encrypted_year

          connection.execute("UPDATE profiles SET #{update_sql.join(', ')} WHERE id = #{profile.id}") if update_sql.any?
        end
      end
    end

    # Disable support for unencrypted data - now all data should be encrypted
    ActiveRecord::Encryption.config.support_unencrypted_data = false
  end

  def down
    say 'Rollback: Remove encrypts declarations from Profile model manually to read the data'
    say 'Then convert year_of_birth back to integer if needed'
  end
end
