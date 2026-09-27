# frozen_string_literal: true

require 'rails_helper'

RSpec.describe 'Anonymous mask proposals', type: :request do
  include Devise::Test::IntegrationHelpers
  include ActiveJob::TestHelper

  let(:admin) do
    User.create!(email: 'proposal-admin@example.test', password: 'test-password-123',
                 confirmed_at: Time.current, admin: true)
  end
  let(:mask) { Mask.create!(author: admin, unique_internal_model_code: 'Zimi B95-XL') }
  let(:test_data) do
    { exercises: { '1' => 211 }, final: 211, status: 'completed', mask: 'Zimi B95-XL-01 White',
      protocol_name: 'w1', propose_mask: true }
  end
  let(:payload) do
    { contribution_id: SecureRandom.uuid, measurement_version: 1,
      measurements: { nose_mm: 45, strap_mm: 130, top_cheek_mm: 98, mid_cheek_mm: 90, chin_mm: 100 },
      fit_tests: [test_data], consent_version: AnonymousContributionPayload::CONSENT_VERSION,
      consent_accepted_at: Time.current.utc.iso8601 }
  end

  before { ActiveJob::Base.queue_adapter = :test }
  after { clear_enqueued_jobs }

  def submit(data = payload)
    post '/anonymous_contributions', params: { contribution: data },
                                     headers: { 'Authorization' => "Bearer #{'c' * 64}" }, as: :json
  end

  it 'suggests canonical masks, ranks the intended size first, and creates no proposals' do
    mask
    Mask.create!(author: admin, unique_internal_model_code: 'Zimi B95-S')
    Mask.create!(author: admin, unique_internal_model_code: 'Zimi B95-XL White duplicate', duplicate_of: mask.id)
    expect do
      get '/anonymous_contributions/mask_suggestions', params: { name: 'Zimi B95-XL-01 White' }
    end.not_to change(MaskProposal, :count)
    expect(response).to have_http_status(:ok)
    expect(response.parsed_body['masks'].first['id']).to eq(mask.id)
    expect(response.parsed_body['masks'].map { |row| row['name'] }).not_to include('Zimi B95-XL White duplicate')
    expect(enqueued_jobs).to be_empty
  end

  it 'validates suggestion names and excludes duplicates from catalog search' do
    get '/anonymous_contributions/mask_suggestions', params: { name: 'x' * 201 }
    expect(response).to have_http_status(:unprocessable_entity)
    mask
    Mask.create!(author: admin, unique_internal_model_code: 'Zimi duplicate', duplicate_of: mask.id)
    get '/anonymous_contributions/masks', params: { search: 'Zimi' }
    expect(response.parsed_body['masks'].pluck('id')).to eq([mask.id])
  end

  it 'groups repeated names, preserves each test, and enqueues one notification across retries' do
    submit(payload.merge(fit_tests: [test_data, test_data.merge(mask: ' zimi   b95-xl-01 white ')]))
    expect(response).to have_http_status(:ok)
    expect(MaskProposal.count).to eq(1)
    expect(MaskProposalLink.count).to eq(2)
    expect(enqueued_jobs.count { |job| job[:job] == MaskProposalNotificationJob }).to eq(1)
    submit(payload.merge(fit_tests: [test_data, test_data.merge(mask: ' zimi   b95-xl-01 white ')]))
    expect(response).to have_http_status(:ok)
    expect(MaskProposalLink.count).to eq(2)
    submit(payload.merge(contribution_id: SecureRandom.uuid))
    expect(MaskProposal.count).to eq(1)
    expect(MaskProposalLink.count).to eq(3)
    expect(enqueued_jobs.count { |job| job[:job] == MaskProposalNotificationJob }).to eq(1)
  end

  it 'keeps legacy unresolved and user-confirmed matches without proposals' do
    submit(payload.merge(fit_tests: [test_data.except(:propose_mask),
                                     test_data.except(:propose_mask).merge(mask_id: mask.id,
                                                                           mask: mask.unique_internal_model_code)]))
    expect(response).to have_http_status(:ok)
    expect(MaskProposal.count).to eq(0)
    expect(AnonymousContribution.last.fit_tests.last['mask_id']).to eq(mask.id)
  end

  it 'rejects empty proposals, ambiguous matches, non-booleans, and unapproved fields atomically' do
    [test_data.merge(mask: ' '), test_data.merge(mask_id: mask.id), test_data.merge(propose_mask: 'true'),
     test_data.merge(mask: '㍿' * 200), test_data.merge(notes: 'identity')].each do |invalid|
      submit(payload.merge(fit_tests: [test_data, invalid]))
      expect(response).to have_http_status(:unprocessable_entity)
    end
    expect(MaskProposal.count).to eq(0)
    expect(AnonymousContribution.count).to eq(0)
  end

  it 'restricts proposal reads and decisions to admins' do
    submit
    get '/admin/mask_proposals.json'
    expect(response).to have_http_status(:unauthorized)
    user = User.create!(email: 'proposal-user@example.test', password: 'test-password-123', confirmed_at: Time.current)
    sign_in user
    get '/admin/mask_proposals.json'
    expect(response).to have_http_status(:forbidden)
    patch "/admin/mask_proposals/#{MaskProposal.last.id}.json", params: { mask_id: mask.id }, as: :json
    expect(response).to have_http_status(:forbidden)
    expect(MaskProposal.last.resolved_at).to be_nil
  end

  it 'matches all linked tests, preserves unrelated tests and measurements, and keeps original retries idempotent' do
    data = payload.merge(fit_tests: [test_data, test_data.except(:propose_mask).merge(mask: 'Other mask')])
    submit(data)
    contribution = AnonymousContribution.last
    original_digest = contribution.payload_digest
    submit(payload.merge(contribution_id: SecureRandom.uuid))
    sign_in admin
    patch "/admin/mask_proposals/#{MaskProposal.last.id}.json", params: { mask_id: mask.id }, as: :json
    expect(response).to have_http_status(:ok)
    expect(contribution.reload.fit_tests.first['mask_id']).to eq(mask.id)
    expect(contribution.fit_tests.first['mask']).to eq('Zimi B95-XL')
    expect(contribution.fit_tests.last['mask']).to eq('Other mask')
    expect(contribution.measurements).to eq(payload[:measurements].stringify_keys)
    expect(contribution.payload_digest).to eq(original_digest)
    expect(AnonymousContribution.last.fit_tests.first['mask_id']).to eq(mask.id)
    submit(data)
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.count).to eq(2)
    submit(data.merge(measurements: payload[:measurements].merge(nose_mm: 46)))
    expect(response).to have_http_status(:conflict)
    submit(payload.merge(contribution_id: SecureRandom.uuid))
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.first['mask_id']).to eq(mask.id)
  end

  it 'creates one reviewed catalog mask and refuses stale review decisions' do
    submit
    sign_in admin
    proposal = MaskProposal.last
    expect do
      patch "/admin/mask_proposals/#{proposal.id}.json", params: { name: 'New Zimi model XL' }, as: :json
    end.to change(Mask, :count).by(1)
    expect(response).to have_http_status(:ok)
    expect(proposal.reload.reviewer).to eq(admin)
    expect(AnonymousContribution.last.fit_tests.first['mask_id']).to eq(proposal.mask_id)
    expect do
      patch "/admin/mask_proposals/#{proposal.id}.json", params: { name: 'Another name' }, as: :json
    end.not_to change(Mask, :count)
    expect(response).to have_http_status(:conflict)
    get '/admin/mask_proposals.json'
    expect(response.parsed_body['proposals']).to be_empty
    get '/admin/mask_proposals.json', params: { include_resolved: true, id: proposal.id }
    expect(response.parsed_body['proposals'].first['mask_name']).to eq('New Zimi model XL')
    expect(response.parsed_body.to_s).not_to include('nose_mm', 'credential')
  end

  it 'leaves proposals pending after invalid admin decisions' do
    submit
    sign_in admin
    patch "/admin/mask_proposals/#{MaskProposal.last.id}.json", params: { name: ' ' }, as: :json
    expect(response).to have_http_status(:unprocessable_entity)
    patch "/admin/mask_proposals/#{MaskProposal.last.id}.json", params: { mask_id: -1 }, as: :json
    expect(response).to have_http_status(:not_found)
    expect(MaskProposal.last.resolved_at).to be_nil
    expect(AnonymousContribution.last.fit_tests.first['mask_id']).to be_nil
  end

  it 'preserves earlier decisions when two proposals share a contribution' do
    submit(payload.merge(fit_tests: [test_data, test_data.merge(mask: 'Another model')]))
    sign_in admin
    proposals = [MaskProposal.find_by!(name: test_data[:mask]), MaskProposal.find_by!(name: 'Another model')]
    patch "/admin/mask_proposals/#{proposals.first.id}.json", params: { mask_id: mask.id }, as: :json
    patch "/admin/mask_proposals/#{proposals.last.id}.json", params: { name: 'Another reviewed model' }, as: :json
    expect(response).to have_http_status(:ok)
    expect(AnonymousContribution.last.fit_tests.pluck('mask_id')).to eq(proposals.map { |row| row.reload.mask_id })
  end

  it 'does not orphan proposals or notifications when ingestion rolls back' do
    allow(AnonymousMaskProposals).to receive(:attach!).and_wrap_original do |original, contribution|
      original.call(contribution)
      raise ActiveRecord::RecordInvalid
    end
    expect { submit }.to raise_error(ActiveRecord::RecordInvalid)
    expect(MaskProposal.count).to eq(0)
    expect(AnonymousContribution.count).to eq(0)
    expect(enqueued_jobs).to be_empty
  end

  it 'notifies admins once on job retries without disclosing participant data' do
    admin
    submit
    proposal = MaskProposal.last
    expect do
      2.times { MaskProposalNotificationJob.perform_now(proposal.id) }
    end.to change(ActionMailer::Base.deliveries, :size).by(1)
    message = ActionMailer::Base.deliveries.last
    expect(message.bcc).to include(admin.email)
    expect(message.body.decoded).to include(proposal.name, '/#/admin/masks/proposals?proposal=')
    expect(message.body.decoded).not_to include('nose_mm', 'strap_mm', payload[:contribution_id])
    expect(proposal.reload.notified_at).to be_present
  end
end
