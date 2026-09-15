# frozen_string_literal: true

# A strict allowlist shared by ingestion and the research export's stored format.
# Never persist raw MFTC payloads or arbitrary source fields.
class AnonymousContributionPayload
  class Invalid < StandardError; end

  CONSENT_VERSION = 'anonymous-2026-09-14'
  KEYS = %w[contribution_id measurement_version measurements fit_tests consent_version consent_accepted_at].freeze
  MEASUREMENTS = %w[nose_mm strap_mm top_cheek_mm mid_cheek_mm chin_mm].freeze
  TEST_KEYS = %w[exercises final status mask protocol_name mask_id].freeze

  def self.call(payload)
    new.call(payload)
  end

  def call(payload)
    exact_keys!(payload, KEYS)
    invalid! unless payload['contribution_id'].is_a?(String) &&
                    payload['contribution_id'].match?(/\A[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\z/i)
    invalid! unless payload['measurement_version'] == 1 && payload['measurement_version'].is_a?(Integer)
    invalid! unless payload['consent_version'] == CONSENT_VERSION
    invalid! unless payload['consent_accepted_at'].is_a?(String)
    accepted_at = Time.iso8601(payload['consent_accepted_at'])
    invalid! if accepted_at > 1.day.from_now
    exact_keys!(payload['measurements'], MEASUREMENTS)
    invalid! unless payload['measurements'].values.all? { |value| positive_number?(value) }
    tests = payload['fit_tests']
    invalid! unless tests.is_a?(Array) && tests.size <= 100
    tests.each { |test| validate_test!(test) }
    payload.merge('contribution_id' => payload['contribution_id'].downcase,
                  'consent_accepted_at' => accepted_at.utc.iso8601)
  rescue ArgumentError, TypeError
    invalid!
  end

  private

  def validate_test!(test)
    invalid! unless test.is_a?(Hash) && (test.keys - TEST_KEYS).empty?
    invalid! unless %w[exercises status mask protocol_name].all? { |key| test.key?(key) }
    exercises = test['exercises']
    invalid! unless exercises.is_a?(Hash) && exercises.size <= 12 &&
                    exercises.all? { |key, value| key.match?(/\A(?:[1-9]|1[0-2])\z/) && positive_number?(value) }
    final = test['final']
    invalid! unless final.nil? || positive_number?(final)
    invalid! unless test['status'] == (final.nil? ? 'incomplete' : 'completed')
    %w[mask protocol_name].each do |field|
      value = test[field]
      invalid! unless value.is_a?(String) && value.length <= 200 && !value.match?(/[[:cntrl:]]/)
    end
    return if test['mask_id'].nil?

    invalid! unless test['mask_id'].is_a?(Integer) && Mask.exists?(id: test['mask_id'])
  end

  def exact_keys!(hash, keys)
    invalid! unless hash.is_a?(Hash) && hash.keys.sort == keys.sort
  end

  def positive_number?(value)
    value.is_a?(Numeric) && value.finite? && value.positive?
  end

  def invalid!
    raise Invalid, 'Invalid contribution. Check measurements, fit-test fields, and consent version.'
  end
end
