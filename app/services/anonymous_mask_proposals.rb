# frozen_string_literal: true

class AnonymousMaskProposals
  def self.attach!(contribution)
    tests = contribution.fit_tests.each_with_index.select { |test, _| test['propose_mask'] == true }
    # Stable lock order for submissions proposing several masks at once.
    tests.sort_by { |test, _| MaskProposal.normalize(test['mask']) }.each do |test, index|
      key = MaskProposal.normalize(test['mask'])
      proposal = MaskProposal.create_or_find_by!(normalized_name: key) { |row| row.name = test['mask'].strip }
      proposal.with_lock do
        proposal.mask_proposal_links.create!(anonymous_contribution: contribution, test_index: index)
        proposal.apply_to!(contribution, index)
      end
    end
  end
end
