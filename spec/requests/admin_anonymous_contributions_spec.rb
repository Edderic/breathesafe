# frozen_string_literal: true

require 'rails_helper'

RSpec.describe 'Admin anonymous submissions', type: :request do
  include Devise::Test::IntegrationHelpers
  include ActiveSupport::Testing::TimeHelpers

  let(:admin) do
    User.create!(email: 'cleanup-admin@example.test', password: 'test-password-123',
                 confirmed_at: Time.current, admin: true)
  end
  let(:participant) { AnonymousParticipant.create!(credential_digest: 'a' * 64) }
  let(:base) { '/admin/anonymous_contributions' }

  def contribution(source: nil, tests: [])
    AnonymousContribution.create!(anonymous_participant: participant, contribution_id: SecureRandom.uuid,
                                  measurement_version: 1, measurements: { nose_mm: 90 }, fit_tests: tests,
                                  measurement_source_contribution_id: source&.contribution_id,
                                  consent_version: 'test', consent_accepted_at: Time.current,
                                  payload_digest: SecureRandom.hex(32))
  end

  def preview(*rows)
    post "#{base}/deletion_preview.json", params: { contribution_ids: rows.map(&:contribution_id) }, as: :json
    response.parsed_body['token']
  end

  def remove(token)
    delete "#{base}/destroy_selected.json", params: { token: token }, as: :json
  end

  it 'requires authentication and admin privileges for every endpoint' do
    [nil, User.create!(email: 'cleanup-user@example.test', password: 'test-password-123',
                       confirmed_at: Time.current)].each do |user|
      sign_in user if user
      expected = user ? :forbidden : :unauthorized
      get "#{base}.json"
      expect(response).to have_http_status(expected)
      post "#{base}/deletion_preview.json", params: { contribution_ids: [] }, as: :json
      expect(response).to have_http_status(expected)
      remove('invalid')
      expect(response).to have_http_status(expected)
    end
  end

  it 'lists newest first with bounded cursor pagination and excludes internal digests' do
    sign_in admin
    rows = Array.new(26) { contribution }
    get "#{base}.json"
    data = response.parsed_body
    expect(data['contributions'].pluck('contribution_id')).to eq(rows.reverse.first(25).map(&:contribution_id))
    expect(data['has_more']).to be(true)
    expect(response.headers['Cache-Control']).to include('no-store')
    expect(response.body).not_to include('payload_digest', 'credential_digest')
    get "#{base}.json", params: { before_id: data['contributions'].last['id'] }
    expect(response.parsed_body['contributions'].pluck('contribution_id')).to eq([rows.first.contribution_id])
    expect(response.parsed_body['has_more']).to be(false)
  end

  it 'filters by exact receipt and participant and validates filters' do
    sign_in admin
    row = contribution
    contribution
    get "#{base}.json", params: { receipt: row.contribution_id.upcase, participant: participant.id }
    expect(response.parsed_body['contributions'].pluck('contribution_id')).to eq([row.contribution_id])
    get "#{base}.json", params: { participant: participant.id + 1 }
    expect(response.parsed_body['contributions']).to eq([])
    [{ receipt: 'invalid' }, { participant: 'all' }, { before_id: 'invalid' }].each do |filters|
      get "#{base}.json", params: filters
      expect(response).to have_http_status(:unprocessable_entity)
    end
  end

  it 'previews without deleting, then removes only selected contributions and proposal links' do
    sign_in admin
    row = contribution(tests: [{ 'mask' => 'Test mask', 'final' => 99 }])
    retained = contribution
    proposal = MaskProposal.create!(name: 'Test mask', normalized_name: 'test mask')
    MaskProposalLink.create!(mask_proposal: proposal, anonymous_contribution: row, test_index: 0)
    token = preview(row)
    expect(response).to have_http_status(:ok)
    expect(response.parsed_body['fit_test_count']).to eq(1)
    expect(AnonymousContribution.count).to eq(2)
    expect { remove(token) }.to change(AnonymousContribution, :count).by(-1)
    expect(response).to have_http_status(:ok)
    expect(response.parsed_body['deleted_ids']).to eq([row.contribution_id])
    expect(MaskProposalLink.count).to eq(0)
    expect(MaskProposal.exists?(proposal.id)).to be(true)
    expect(AnonymousParticipant.exists?(participant.id)).to be(true)
    expect(AnonymousContribution.exists?(retained.id)).to be(true)
  end

  it 'rejects invalid, empty, oversized, and partially missing selections without deleting' do
    sign_in admin
    row = contribution
    [nil, [], 'all', ['invalid'], Array.new(101, row.contribution_id),
     [row.contribution_id, SecureRandom.uuid]].each do |ids|
      post "#{base}/deletion_preview.json", params: { contribution_ids: ids }, as: :json
      expect(response).to have_http_status(:conflict)
      expect(AnonymousContribution.exists?(row.id)).to be(true)
    end
  end

  it 'blocks deletion of source measurements while retained submissions reuse them' do
    sign_in admin
    source = contribution
    dependent = contribution(source: source)
    preview(source)
    expect(response).to have_http_status(:conflict)
    expect(response.parsed_body['dependent_ids']).to eq([dependent.contribution_id])
    expect(AnonymousContribution.count).to eq(2)
    token = preview(source, dependent)
    remove(token)
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.count).to eq(0)
  end

  it 'rechecks new dependencies after preview' do
    sign_in admin
    source = contribution
    token = preview(source)
    contribution(source: source)
    remove(token)
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.count).to eq(2)
  end

  it 'rejects changed submissions and replayed previews' do
    sign_in admin
    row = contribution
    token = preview(row)
    row.update!(fit_tests: [{ 'mask' => 'Reviewed mask', 'final' => 5 }])
    remove(token)
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.exists?(row.id)).to be(true)
    token = preview(row)
    remove(token)
    expect(response).to have_http_status(:ok)
    remove(token)
    expect(response).to have_http_status(:conflict)
  end

  it 'rejects missing, tampered, expired, and another admin’s previews' do
    sign_in admin
    row = contribution
    token = preview(row)
    [nil, "#{token}changed"].each do |invalid|
      remove(invalid)
      expect(response).to have_http_status(:conflict)
    end
    travel 16.minutes do
      remove(token)
      expect(response).to have_http_status(:conflict)
    end
    other_admin = User.create!(email: 'other-cleanup-admin@example.test', password: 'test-password-123',
                               confirmed_at: Time.current, admin: true)
    sign_in other_admin
    remove(token)
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.exists?(row.id)).to be(true)
  end

  it 'rolls back earlier deletions when a selected record fails to destroy' do
    sign_in admin
    first = contribution
    second = contribution
    token = preview(first, second)
    callback = ->(row) { throw(:abort) if row.id == second.id }
    AnonymousContribution.set_callback(:destroy, :before, callback)
    remove(token)
    expect(response).to have_http_status(:conflict)
    expect(AnonymousContribution.count).to eq(2)
  ensure
    AnonymousContribution.skip_callback(:destroy, :before, callback)
  end
end
