# frozen_string_literal: true

class MaskFitTestSummaryService
  def self.call(viewer:, target_user_id:, mask_ids:)
    new(viewer:, target_user_id:, mask_ids:).call
  end

  def initialize(viewer:, target_user_id:, mask_ids:)
    @viewer = viewer
    @target_user_id = target_user_id.to_i
    @mask_ids = Array(mask_ids).map(&:to_i).uniq
  end

  def call
    return {} if mask_ids.empty?
    raise StandardError, 'unauthorized' unless viewer

    user = User.find(target_user_id)
    raise StandardError, 'forbidden' unless viewer.manages?(user)

    matching_rows = fit_test_rows.select do |row|
      row['user_id'].to_i == target_user_id &&
        target_fit_family_ids.include?(fit_family_identity_for(row))
    end

    summaries_by_fit_family = matching_rows
                              .group_by { |row| fit_family_identity_for(row) }
                              .transform_values { |rows| summarize(rows) }

    mask_ids.index_with do |mask_id|
      summaries_by_fit_family[fit_family_id_by_mask_id[mask_id]]
    end.compact
  end

  private

  attr_reader :viewer, :target_user_id, :mask_ids

  def fit_test_rows
    @fit_test_rows ||= FitTestsWithFacialMeasurementsService.call
  end

  def fit_family_id_by_mask_id
    @fit_family_id_by_mask_id ||= Mask.where(id: mask_ids).pluck(:id, :fit_family_id).to_h.transform_keys(&:to_i)
  end

  def target_fit_family_ids
    @target_fit_family_ids ||= fit_family_id_by_mask_id.values.compact.uniq
  end

  def fit_family_identity_for(row)
    (row['fit_family_id'] || row[:fit_family_id] || row['mask_id'] || row[:mask_id]).to_i
  end

  def summarize(rows)
    latest_row = rows.max_by { |row| sortable_created_at(row['created_at']) }
    evaluable_rows = rows.map do |row|
      normalized = normalize_bool(row['qlft_pass'])
      normalized
    end.compact
    fit_test_count = evaluable_rows.length
    pass_count = evaluable_rows.count(true)
    pass_rate = fit_test_count.positive? ? pass_count.to_f / fit_test_count : nil

    {
      'latest_fit_test_id' => latest_row['id'],
      'latest_fit_test_at' => iso8601_time(latest_row['created_at']),
      'observed_fit_pass_count' => pass_count,
      'observed_fit_test_count' => fit_test_count,
      'observed_fit_pass_rate' => pass_rate,
      'observed_fit_label' => observed_fit_label(pass_count:, fit_test_count:, pass_rate:)
    }
  end

  def normalize_bool(value)
    return true if [true, 't'].include?(value)
    return false if [false, 'f'].include?(value)

    nil
  end

  def observed_fit_label(pass_count:, fit_test_count:, pass_rate:)
    return 'No fit test' if fit_test_count.zero? || pass_rate.nil?

    "#{(pass_rate * 100).round}% (#{pass_count}/#{fit_test_count})"
  end

  def iso8601_time(value)
    return nil if value.blank?
    return value.iso8601 if value.respond_to?(:iso8601)

    Time.zone.parse(value.to_s)&.iso8601
  rescue ArgumentError, TypeError
    value.to_s
  end

  def sortable_created_at(value)
    return value if value.respond_to?(:to_time)

    Time.zone.parse(value.to_s)
  rescue ArgumentError, TypeError
    Time.zone.at(0)
  end
end
