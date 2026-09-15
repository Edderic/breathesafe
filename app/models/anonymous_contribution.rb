# frozen_string_literal: true

class AnonymousContribution < ApplicationRecord
  belongs_to :anonymous_participant
  validates :contribution_id, :consent_version, :consent_accepted_at, :payload_digest, presence: true
  validates :measurement_version, inclusion: { in: [1] }
end
