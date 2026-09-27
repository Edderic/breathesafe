# frozen_string_literal: true

namespace :mask_proposals do
  desc 'Retry undelivered admin notifications (safe to repeat)'
  task notify_pending: :environment do
    MaskProposal.where(notified_at: nil).find_each { |proposal| MaskProposalNotificationJob.perform_later(proposal.id) }
  end
end
