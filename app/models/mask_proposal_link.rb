# frozen_string_literal: true

class MaskProposalLink < ApplicationRecord
  belongs_to :mask_proposal
  belongs_to :anonymous_contribution
end
