# frozen_string_literal: true

class EncryptProfileDemographicFields < ActiveRecord::Migration[7.0]
  # Create a version of Profile without encryption to read raw values
  class ProfileWithoutEncryption < ApplicationRecord
    self.table_name = 'profiles'
    # Don't use any encryption
  end

  def up
    # Enable support for unencrypted data so Rails can read the current values
    # and encrypt them on save
    original_config = ActiveRecord::Encryption.config.support_unencrypted_data
    ActiveRecord::Encryption.config.support_unencrypted_data = true

    say_with_time "Encrypting demographic fields for #{ProfileWithoutEncryption.count} profiles" do
      ProfileWithoutEncryption.find_each do |profile_raw|
        # Read raw unencrypted values directly from database
        raw_race_ethnicity = profile_raw.attributes['race_ethnicity']
        raw_gender_and_sex = profile_raw.attributes['gender_and_sex']
        raw_other_gender = profile_raw.attributes['other_gender']
        raw_year_of_birth = profile_raw.attributes['year_of_birth']

        # Now update using the encrypted Profile model
        # This will encrypt the values when saving
        Profile.where(id: profile_raw.id).update_all(
          race_ethnicity: Profile.type_for_attribute(:race_ethnicity).serialize(raw_race_ethnicity),
          gender_and_sex: Profile.type_for_attribute(:gender_and_sex).serialize(raw_gender_and_sex),
          other_gender: Profile.type_for_attribute(:other_gender).serialize(raw_other_gender),
          year_of_birth: Profile.type_for_attribute(:year_of_birth).serialize(raw_year_of_birth)
        )
      end
    end

    # Restore original config
    ActiveRecord::Encryption.config.support_unencrypted_data = original_config
  end

  def down
    # No need to decrypt on rollback since the data is still accessible
    # The encrypts declarations would need to be removed from the model
    say 'Rollback: Remove encrypts declarations from Profile model manually'
  end
end
