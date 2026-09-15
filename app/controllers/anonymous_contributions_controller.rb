# frozen_string_literal: true

require 'digest'

# No account session, cookies, or identity lookup is used by this endpoint.
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

  # Deliberately avoids the expensive fit-test aggregation used by the main catalog.
  def masks
    page = params[:page].to_i.clamp(1, 10_000)
    scope = Mask.order(:id)
    search = params[:search].to_s.strip.first(200)
    scope = scope.where('unique_internal_model_code ILIKE ?', "%#{Mask.sanitize_sql_like(search)}%") if search.present?
    rows = scope.offset((page - 1) * 50).limit(51).pluck(:id, :unique_internal_model_code)
    render json: { masks: rows.first(50).map { |id, name| { id: id, name: name.to_s } }, has_more: rows.size > 50 }
  end

  private

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
