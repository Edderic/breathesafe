# frozen_string_literal: true

class AnonymousParticipant < ApplicationRecord
  has_many :anonymous_contributions, dependent: :restrict_with_exception
  validates :credential_digest, presence: true, format: { with: /\A[0-9a-f]{64}\z/ }
end
