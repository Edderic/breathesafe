# frozen_string_literal: true

class MaskProposalMailer < ApplicationMailer
  default from: 'info@breathesafe.xyz'

  def review(proposal, recipients)
    # No participant identifiers, measurements, or fit-test results in notifications.
    options = Rails.application.config.action_mailer.default_url_options || {}
    host = options[:host] || 'www.breathesafe.xyz'
    link = "https://#{host}/#/admin/masks/proposals?proposal=#{proposal.id}"
    mail(bcc: recipients, subject: 'New mask proposal to review') do |format|
      format.text do
        render plain: "Proposed mask: #{proposal.name}\n\nReview and match or create a catalog mask:\n#{link}"
      end
    end
  end
end
