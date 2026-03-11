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

    fit_test_rows
      .select { |row| row['user_id'].to_i == target_user_id && mask_ids.include?(row['mask_id'].to_i) }
      .group_by { |row| row['mask_id'].to_i }
      .transform_values { |rows| summarize(rows.max_by { |row| row['created_at'] || Time.zone.at(0) }) }
  end

  private

  attr_reader :viewer, :target_user_id, :mask_ids

  def fit_test_rows
    @fit_test_rows ||= FitTestsWithFacialMeasurementsService.call
  end

  def summarize(row)
    qlft_pass = normalize_bool(row['qlft_pass'])
    n95_mode_hmff = row['n95_mode_hmff'].present? ? row['n95_mode_hmff'].to_f : nil
    procedure = row['procedure'].presence
    testing_mode = row.dig('results', 'quantitative', 'testing_mode').presence

    {
      'latest_fit_test_id' => row['id'],
      'latest_fit_test_at' => iso8601_time(row['created_at']),
      'qlft_pass' => qlft_pass,
      'n95_mode_hmff' => n95_mode_hmff,
      'n95_mode_source' => n95_mode_source(testing_mode),
      'procedure' => procedure,
      'observed_fit_label' => observed_fit_label(qlft_pass:, n95_mode_hmff:, testing_mode:)
    }
  end

  def normalize_bool(value)
    return true if [true, 't'].include?(value)
    return false if [false, 'f'].include?(value)

    nil
  end

  def n95_mode_source(testing_mode)
    return 'actual' if testing_mode == 'N95'
    return 'converted' if testing_mode == 'N99'

    nil
  end

  def observed_fit_label(qlft_pass:, n95_mode_hmff:, testing_mode:)
    return "N95 mode #{n95_mode_hmff.round} (actual)" if n95_mode_hmff && testing_mode == 'N95'
    return "N95 mode #{n95_mode_hmff.round} (converted)" if n95_mode_hmff && testing_mode == 'N99'
    return 'QLFT Pass' if qlft_pass == true
    return 'QLFT Fail' if qlft_pass == false

    'No fit test'
  end

  def iso8601_time(value)
    return nil if value.blank?
    return value.iso8601 if value.respond_to?(:iso8601)

    Time.zone.parse(value.to_s)&.iso8601
  rescue ArgumentError, TypeError
    value.to_s
  end
end
