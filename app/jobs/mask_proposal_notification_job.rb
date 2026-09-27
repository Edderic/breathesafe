# frozen_string_literal: true

class MaskProposalNotificationJob < ApplicationJob
  def perform(proposal_id)
    proposal = MaskProposal.find(proposal_id)
    proposal.with_lock do
      return if proposal.notified_at

      recipients = User.where(admin: true).where.not(confirmed_at: nil).pluck(:email)
      return if recipients.empty?

      MaskProposalMailer.review(proposal, recipients).deliver_now
      proposal.update!(notified_at: Time.current)
    end
  end
end
