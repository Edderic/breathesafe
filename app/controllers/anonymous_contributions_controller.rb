# frozen_string_literal: true

require 'digest'

# Participant codes authenticate requests independently of account sessions and cookies.
class AnonymousContributionsController < ActionController::API
  wrap_parameters false

  def create
    credential = request.authorization.to_s.delete_prefix('Bearer ')
    unless credential.match?(/\A[0-9a-f]{64}\z/)
      return render json: { error: 'Invalid participant code' }, status: :unauthorized
    end

    envelope = request.request_parameters
    raise AnonymousContributionPayload::Invalid unless envelope.keys == ['contribution']

    payload = AnonymousContributionPayload.call(envelope['contribution'])
    digest = Digest::SHA256.hexdigest(credential)
    payload_digest = Digest::SHA256.hexdigest(canonical_json(payload))
    participant = AnonymousParticipant.create_or_find_by!(credential_digest: digest)
    records = participant.anonymous_contributions
    validate_measurement_source!(records, payload)
    record = records.create_or_find_by!(contribution_id: payload['contribution_id']) do |row|
      row.assign_attributes(payload.except('contribution_id'))
      row.payload_digest = payload_digest
    end
    unless record.payload_digest == payload_digest
      return render json: { error: 'Receipt conflicts with an existing submission' }, status: :conflict
    end

    render json: { contribution_id: record.contribution_id, status: 'submitted' }, status: :ok
  rescue AnonymousContributionPayload::Invalid
    render json: { error: 'Invalid contribution. Check the reviewed data and consent version.' },
           status: :unprocessable_entity
  rescue ActiveRecord::RecordNotFound, ActiveRecord::RecordNotUnique
    # A contribution UUID belonging to a different participant is never disclosed.
    render json: { error: 'Receipt conflicts with an existing submission' }, status: :conflict
  end

  # Never creates a participant or returns fit-test history. The code is a bearer secret.
  def previous_measurements
    response.headers['Cache-Control'] = 'no-store'
    credential = request.authorization.to_s.delete_prefix('Bearer ')
    unless credential.match?(/\A[0-9a-f]{64}\z/)
      return render json: { error: 'Invalid participant code' }, status: :unauthorized
    end

    participant = AnonymousParticipant.find_by(credential_digest: Digest::SHA256.hexdigest(credential))
    # Reused submissions must not make an older scan look newer. Consent time is
    # the original submission time, not a claim about the exact time of capture.
    source = participant&.anonymous_contributions
                        &.where(measurement_source_contribution_id: nil, measurement_version: 1)
                        &.order(consent_accepted_at: :desc, id: :desc)&.first
    render json: { previous_measurements: source&.attributes&.slice(
      'contribution_id', 'measurement_version', 'measurements', 'consent_accepted_at'
    ) }
  end

  # Deliberately avoids the expensive fit-test aggregation used by the main catalog.
  def masks
    page = params[:page].to_i.clamp(1, 10_000)
    scope = Mask.where(duplicate_of: nil).order(:id)
    search = params[:search].to_s.strip.first(200)
    scope = scope.where('unique_internal_model_code ILIKE ?', "%#{Mask.sanitize_sql_like(search)}%") if search.present?
    rows = scope.offset((page - 1) * 50).limit(51).pluck(:id, :unique_internal_model_code)
    render json: { masks: rows.first(50).map { |id, name| { id: id, name: name.to_s } }, has_more: rows.size > 50 }
  end

  def mask_suggestions
    name = params[:name].to_s.strip
    if name.empty? || name.length > 200 || name.match?(/[[:cntrl:]]/)
      return render json: { error: 'Enter a mask model name.' }, status: :unprocessable_entity
    end

    render json: { masks: MaskMatching::AnonymousSuggestions.call(name) }
  end

  private

  def validate_measurement_source!(records, payload)
    return unless payload.key?('measurement_source_contribution_id')

    source = records.find_by(contribution_id: payload['measurement_source_contribution_id'],
                             measurement_source_contribution_id: nil)
    return if source && source.measurement_version == payload['measurement_version'] &&
              source.measurements == payload['measurements']

    raise AnonymousContributionPayload::Invalid
  end

  def canonical_json(value)
    case value
    when Hash
      entries = value.keys.sort.map { |key| "#{key.to_json}:#{canonical_json(value[key])}" }.join(',')
      "{#{entries}}"
    when Array
      "[#{value.map { |element| canonical_json(element) }.join(',')}]"
    else
      value.to_json
    end
  end
end
