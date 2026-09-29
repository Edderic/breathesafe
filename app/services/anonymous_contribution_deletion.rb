# frozen_string_literal: true

class AnonymousContributionDeletion
  class Error < StandardError
    attr_reader :dependent_ids

    def initialize(message, dependent_ids: [])
      @dependent_ids = dependent_ids
      super(message)
    end
  end

  def self.serialize(row)
    row.attributes.slice('id', 'contribution_id', 'anonymous_participant_id', 'created_at',
                         'consent_accepted_at', 'measurement_version', 'measurement_source_contribution_id',
                         'measurements', 'fit_tests')
  end

  def initialize(admin)
    @admin = admin
  end

  def preview(ids)
    with_selection(ids) do |rows|
      {
        contributions: rows.map { |row| self.class.serialize(row) },
        fit_test_count: rows.sum { |row| row.fit_tests.size },
        token: verifier.generate({ admin_id: @admin.id, ids: rows.map(&:contribution_id),
                                   fingerprint: fingerprint(rows) }, expires_in: 15.minutes)
      }
    end
  end

  def delete(token)
    selection = verifier.verified(token.to_s)
    unless selection.is_a?(Hash) && selection[:admin_id] == @admin.id
      raise Error, 'This deletion preview is invalid or expired. Review your selection again.'
    end

    deleted_ids = with_selection(selection[:ids]) do |rows|
      if fingerprint(rows) != selection[:fingerprint]
        raise Error, 'A selected submission changed. Review your selection again before deleting.'
      end

      # Reused snapshots reference originals. Remove them first to respect the foreign key.
      rows.sort_by { |row| row.measurement_source_contribution_id ? 0 : 1 }.each(&:destroy!)
      rows.map(&:contribution_id)
    end
    Rails.logger.info({ event: 'anonymous_contributions_deleted', admin_id: @admin.id,
                        contribution_ids: deleted_ids }.to_json)
    deleted_ids
  end

  private

  def verifier
    Rails.application.message_verifier('admin-anonymous-contribution-deletion')
  end

  def fingerprint(rows)
    Digest::SHA256.hexdigest(rows.map(&:attributes).to_json)
  end

  def with_selection(ids)
    uuid = /\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\z/i
    unless ids.is_a?(Array) && (1..100).cover?(ids.size) && ids.all? { |id| id.is_a?(String) && uuid.match?(id) }
      raise Error, 'Select between 1 and 100 submissions using complete receipt IDs.'
    end

    ids = ids.map(&:downcase).uniq
    AnonymousContribution.transaction do
      rows = AnonymousContribution.where(contribution_id: ids).order(:id).lock.to_a
      raise Error, 'A selected submission no longer exists. Refresh the list.' if rows.size != ids.size

      dependent_ids = AnonymousContribution.where(measurement_source_contribution_id: ids)
                                           .where.not(contribution_id: ids).order(:id).pluck(:contribution_id)
      if dependent_ids.any?
        raise Error.new('Other submissions reuse these measurements. Review those submissions before deleting.',
                        dependent_ids: dependent_ids)
      end

      yield rows
    end
  end
end
