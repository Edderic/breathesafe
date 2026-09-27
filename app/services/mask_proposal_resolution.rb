# frozen_string_literal: true

class MaskProposalResolution
  class AlreadyResolved < StandardError; end

  def self.call(proposal:, reviewer:, mask_id: nil, name: nil)
    proposal.with_lock do
      raise AlreadyResolved, 'This proposal has already been reviewed. Refresh the list.' if proposal.resolved_at

      mask = if mask_id.present?
               Mask.where(duplicate_of: nil).find(mask_id)
             else
               Mask.create!(author: reviewer, unique_internal_model_code: name)
             end
      proposal.update!(mask: mask, reviewer: reviewer, resolved_at: Time.current)
      proposal.mask_proposal_links.order(:anonymous_contribution_id, :test_index).each do |link|
        contribution = link.anonymous_contribution
        contribution.with_lock { proposal.apply_to!(contribution, link.test_index) }
      end
    end
    proposal
  end
end
