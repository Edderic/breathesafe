# frozen_string_literal: true

class MaskProposal < ApplicationRecord
  belongs_to :mask, optional: true
  belongs_to :reviewer, class_name: 'User', optional: true
  has_many :mask_proposal_links, dependent: :destroy
  validates :name, :normalized_name, presence: true, length: { maximum: 200 }
  after_create_commit :notify_admins

  def self.normalize(name)
    name.unicode_normalize(:nfkc).downcase.strip.gsub(/\s+/, ' ')
  end

  # Only admin-reviewed proposals can supply a match without contributor confirmation.
  def apply_to!(contribution, index)
    return unless mask

    tests = contribution.fit_tests.deep_dup
    tests.fetch(index).merge!('mask_id' => mask.id, 'mask' => mask.unique_internal_model_code)
    contribution.update!(fit_tests: tests)
  end

  private

  def notify_admins
    MaskProposalNotificationJob.perform_later(id)
  end
end
