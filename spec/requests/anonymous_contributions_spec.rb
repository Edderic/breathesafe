# frozen_string_literal: true

require 'rails_helper'

RSpec.describe 'Anonymous contributions', type: :request do
  include Devise::Test::IntegrationHelpers
  let(:credential) { 'a' * 64 }
  let(:headers) { { 'Authorization' => "Bearer #{credential}" } }
  let(:payload) do
    {
      contribution_id: SecureRandom.uuid,
      measurement_version: 1,
      measurements: { nose_mm: 80.5, strap_mm: 100, top_cheek_mm: 120, mid_cheek_mm: 130, chin_mm: 90 },
      fit_tests: [],
      consent_version: AnonymousContributionPayload::CONSENT_VERSION,
      consent_accepted_at: Time.current.utc.iso8601
    }
  end

  def submit(data = payload, request_headers = headers)
    post '/anonymous_contributions', params: { contribution: data }, headers: request_headers, as: :json
  end

  it 'accepts measurements without an account or fit test and stores a digest rather than the credential' do
    expect { submit }.to change(AnonymousContribution, :count).by(1)
    expect(response).to have_http_status(:ok)
    expect(response.parsed_body['contribution_id']).to eq(payload[:contribution_id])
    expect(AnonymousParticipant.last.credential_digest).to eq(Digest::SHA256.hexdigest(credential))
    expect(AnonymousContribution.last.measurements.keys).to match_array(payload[:measurements].keys.map(&:to_s))
  end

  it 'reuses the participant and makes a lost-response retry idempotent' do
    submit
    expect { submit }.not_to change(AnonymousContribution, :count)
    expect(response).to have_http_status(:ok)
    expect { submit(payload.merge(contribution_id: SecureRandom.uuid)) }.not_to change(AnonymousParticipant, :count)
    expect(response).to have_http_status(:ok)
  end

  it 'rejects reuse of a receipt with changed data' do
    submit
    submit(payload.merge(measurements: payload[:measurements].merge(nose_mm: 85)))
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.last.measurements['nose_mm']).to eq(80.5)
  end

  it 'does not allow another participant to claim an existing receipt' do
    submit
    submit(payload, { 'Authorization' => "Bearer #{'b' * 64}" })
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.count).to eq(1)
  end

  it 'rejects missing or malformed credentials' do
    submit(payload, {})
    expect(response).to have_http_status(:unauthorized)
    expect(AnonymousContribution.count).to eq(0)
  end

  it 'rejects source identity fields, raw landmarks, and unexpected envelope fields' do
    submit(payload.merge(participant: 'Do not persist'))
    expect(response).to have_http_status(:unprocessable_entity)
    submit(payload.merge(measurements: payload[:measurements].merge(landmark_coordinates: {})))
    expect(response).to have_http_status(:unprocessable_entity)
    post '/anonymous_contributions', params: { contribution: payload, Notes: 'private' }, headers: headers, as: :json
    expect(response).to have_http_status(:unprocessable_entity)
    expect(AnonymousContribution.count).to eq(0)
  end

  it 'requires complete finite positive measurements and current explicit consent' do
    [payload.merge(measurements: payload[:measurements].except(:chin_mm)),
     payload.merge(measurements: payload[:measurements].merge(chin_mm: -1)),
     payload.merge(consent_version: 'old'), payload.except(:consent_accepted_at)].each do |invalid|
      submit(invalid)
      expect(response).to have_http_status(:unprocessable_entity)
    end
  end

  it 'preserves partial tests without inventing a final result' do
    test = { exercises: { '1' => 45 }, status: 'incomplete', mask: 'Example mask', protocol_name: '4-ex w1.0' }
    submit(payload.merge(fit_tests: [test]))
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.first['status']).to eq('incomplete')
    expect(AnonymousContribution.last.fit_tests.first['final']).to be_nil
  end

  it 'preserves tests aborted before an exercise completed' do
    test = { exercises: {}, status: 'incomplete', mask: '', protocol_name: '' }
    submit(payload.merge(fit_tests: [test]))
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.first['exercises']).to eq({})
  end

  it 'rejects identity fields and inconsistent final status in fit tests' do
    test = { exercises: { '1' => 45 }, status: 'completed', mask: '', protocol_name: '' }
    submit(payload.merge(fit_tests: [test]))
    expect(response).to have_http_status(:unprocessable_entity)
    submit(payload.merge(fit_tests: [test.merge(status: 'incomplete', Notes: 'private')]))
    expect(response).to have_http_status(:unprocessable_entity)
  end

  it 'preserves optional testing modes through storage, retry, and admin export' do
    tests = %w[n95 n99 unknown].map do |mode|
      { exercises: { '1' => 45 }, status: 'incomplete', mask: 'Example', protocol_name: 'w1', testing_mode: mode }
    end
    data = payload.merge(fit_tests: tests)
    submit(data)
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.pluck('testing_mode')).to eq(%w[n95 n99 unknown])
    expect { submit(data) }.not_to change(AnonymousContribution, :count)
    expect(response).to have_http_status(:ok)
    changed = tests.map(&:dup)
    changed.first[:testing_mode] = 'n99'
    submit(data.merge(fit_tests: changed))
    expect(response).to have_http_status(:conflict)
    sign_in User.create!(email: 'mode-export-admin@example.test', password: 'test-password-123',
                         confirmed_at: Time.current, admin: true)
    get '/anonymous_contributions/export'
    expect(response.parsed_body['contributions'].last['fit_tests'].pluck('testing_mode')).to eq(%w[n95 n99 unknown])
  end

  it 'rejects unsupported testing modes and accepts legacy tests without a mode' do
    test = { exercises: {}, status: 'incomplete', mask: 'Example', protocol_name: 'w1' }
    ['N95', 'other', '', nil, 95, true].each do |invalid|
      submit(payload.merge(fit_tests: [test.merge(testing_mode: invalid)]))
      expect(response).to have_http_status(:unprocessable_entity)
    end
    submit(payload.merge(fit_tests: [test]))
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.first).not_to have_key('testing_mode')
    submit(payload.merge(fit_tests: [test]))
    expect(response).to have_http_status(:ok)
  end

  it 'rejects oversized requests before JSON parsing' do
    post '/anonymous_contributions', params: 'x' * 262_145, headers: headers.merge('CONTENT_TYPE' => 'application/json')
    expect(response).to have_http_status(:payload_too_large)
  end

  it 'filters contribution bodies and credentials from Rails parameters' do
    filter = ActiveSupport::ParameterFilter.new(Rails.application.config.filter_parameters)
    filtered = filter.filter('contribution' => payload, 'authorization' => credential)
    expect(filtered.values).to eq(['[FILTERED]', '[FILTERED]'])
  end

  it 'requires an administrator for research exports' do
    get '/anonymous_contributions/export'
    expect(response).to have_http_status(:unauthorized)
    sign_in User.create!(email: 'anonymous-export-user@example.test', password: 'test-password-123',
                         confirmed_at: Time.current)
    get '/anonymous_contributions/export'
    expect(response).to have_http_status(:forbidden)
  end

  it 'exports sanitized data without credential digests to administrators' do
    submit
    sign_in User.create!(email: 'anonymous-export-admin@example.test', password: 'test-password-123',
                         confirmed_at: Time.current, admin: true)
    get '/anonymous_contributions/export'
    expect(response).to have_http_status(:ok)
    row = response.parsed_body['contributions'].first
    expect(row['measurements']['nose_mm']).to eq(80.5)
    expect(row.keys).not_to include('credential_digest', 'payload_digest')
    expect(response.headers['Cache-Control']).to eq('no-store')
  end

  describe 'previous measurements' do
    def lookup(request_headers = headers)
      get '/anonymous_contributions/previous_measurements', headers: request_headers
    end

    it 'requires a valid code and does not create participants during lookup' do
      lookup({})
      expect(response).to have_http_status(:unauthorized)
      expect { lookup }.not_to change(AnonymousParticipant, :count)
      expect(response).to have_http_status(:ok)
      expect(response.parsed_body).to eq('previous_measurements' => nil)
      expect(response.headers['Cache-Control']).to eq('no-store')
    end

    it 'returns only this participant’s aggregates and source metadata' do
      submit
      lookup('Authorization' => "Bearer #{'b' * 64}")
      expect(response.parsed_body['previous_measurements']).to be_nil
      lookup
      source = response.parsed_body['previous_measurements']
      expect(source.keys).to match_array(%w[contribution_id measurement_version measurements consent_accepted_at])
      expect(source['contribution_id']).to eq(payload[:contribution_id])
      expect(source['measurements']).to eq(payload[:measurements].stringify_keys)
      expect(response.headers['Cache-Control']).to eq('no-store')
    end

    it 'keeps reuse tied to the original scan across retries and newer scans' do
      submit
      reused = payload.merge(contribution_id: SecureRandom.uuid,
                             measurement_source_contribution_id: payload[:contribution_id])
      submit(reused)
      expect(response).to have_http_status(:ok)
      expect(AnonymousContribution.last.measurement_source_contribution_id).to eq(payload[:contribution_id])
      lookup
      expect(response.parsed_body['previous_measurements']['contribution_id']).to eq(payload[:contribution_id])
      newer = payload.merge(contribution_id: SecureRandom.uuid, consent_accepted_at: 1.hour.from_now.iso8601,
                            measurements: payload[:measurements].merge(nose_mm: 85))
      submit(newer)
      expect(response).to have_http_status(:ok)
      expect { submit(reused) }.not_to change(AnonymousContribution, :count)
      expect(response).to have_http_status(:ok)
      lookup
      expect(response.parsed_body['previous_measurements']['contribution_id']).to eq(newer[:contribution_id])
    end

    it 'does not replace the latest scan with an older offline scan delivered later' do
      submit
      older = payload.merge(contribution_id: SecureRandom.uuid, consent_accepted_at: 2.days.ago.iso8601)
      submit(older)
      lookup
      expect(response.parsed_body['previous_measurements']['contribution_id']).to eq(payload[:contribution_id])
    end

    it 'rejects another participant’s source, unknown sources, malformed sources, and altered measurements' do
      submit
      reused = payload.merge(contribution_id: SecureRandom.uuid,
                             measurement_source_contribution_id: payload[:contribution_id])
      submit(reused, 'Authorization' => "Bearer #{'b' * 64}")
      expect(response).to have_http_status(:unprocessable_entity)
      [nil, 'invalid', SecureRandom.uuid].each do |source|
        submit(reused.merge(measurement_source_contribution_id: source))
        expect(response).to have_http_status(:unprocessable_entity)
      end
      submit(reused.merge(measurements: payload[:measurements].merge(nose_mm: 81)))
      expect(response).to have_http_status(:unprocessable_entity)
      submit(reused.merge(measurement_version: 2))
      expect(response).to have_http_status(:unprocessable_entity)
      expect(AnonymousContribution.count).to eq(1)
    end

    it 'requires an original source and exports provenance without changing legacy payloads' do
      submit
      original = AnonymousContribution.last
      digest = original.payload_digest
      submit
      expect(original.reload.payload_digest).to eq(digest)
      reused = payload.merge(contribution_id: SecureRandom.uuid,
                             measurement_source_contribution_id: payload[:contribution_id].upcase)
      submit(reused)
      expect(response).to have_http_status(:ok)
      submit(reused.merge(contribution_id: SecureRandom.uuid,
                          measurement_source_contribution_id: reused[:contribution_id]))
      expect(response).to have_http_status(:unprocessable_entity)
      sign_in User.create!(email: 'reuse-export-admin@example.test', password: 'test-password-123',
                           confirmed_at: Time.current, admin: true)
      get '/anonymous_contributions/export'
      rows = response.parsed_body['contributions']
      expect(rows.first['measurement_source_contribution_id']).to be_nil
      expect(rows.last['measurement_source_contribution_id']).to eq(payload[:contribution_id])
    end
  end
end
