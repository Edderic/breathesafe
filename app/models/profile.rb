# frozen_string_literal: true

class Profile < ApplicationRecord
  STRING_DEMOG_FIELDS = %w[race_ethnicity gender_and_sex].freeze
  NUM_DEMOG_FIELDS = ['year_of_birth'].freeze

  belongs_to :user
  validates :user_id, uniqueness: true

  # Encrypt sensitive personal information
  # Using deterministic encryption for first_name and last_name to enable searching
  encrypts :first_name, :last_name, deterministic: true

  before_create do
    self.external_api_token = SecureRandom.uuid
  end
end
