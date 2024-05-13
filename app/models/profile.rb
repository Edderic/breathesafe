class Profile < ApplicationRecord
  belongs_to :user
  validates :user_id, uniqueness: true

  before_create do
    self.external_api_token = SecureRandom.uuid
  end
end
