# frozen_string_literal: true

# Service to calculate dashboard statistics
class DashboardService
  class << self
    def call
      {
        masks: mask_stats,
        fit_tests: fit_test_stats
      }
    end

    private

    def mask_stats
      total_masks = Mask.count

      # Masks with filtration efficiency data OR N99 mode fit test
      masks_with_fe_or_n99 = masks_with_filtration_data
      masks_missing_fe_and_n99 = total_masks - masks_with_fe_or_n99

      # Masks with breathability scores
      masks_with_breathability = count_masks_with_breathability
      masks_without_breathability = total_masks - masks_with_breathability

      {
        total: total_masks,
        with_filtration_data: masks_with_fe_or_n99,
        missing_filtration_data: masks_missing_fe_and_n99,
        with_breathability: masks_with_breathability,
        without_breathability: masks_without_breathability
      }
    end

    def masks_with_filtration_data
      # Use avg_sealed_ff from N99ModeToN95ModeConverterService as the source of truth
      # This includes masks with:
      # 1. Aaron Collins filtration efficiency data, OR
      # 2. N99 mode fit test data with "Normal Breathing (SEALED)" exercise

      avg_sealed_ffs = N99ModeToN95ModeConverterService.avg_sealed_ffs.to_a

      # Get unique mask IDs that have avg_sealed_ff
      mask_ids_with_filtration_data = avg_sealed_ffs.map { |row| row['mask_id'] }.compact.uniq

      mask_ids_with_filtration_data.count
    end

    def count_masks_with_breathability
      # Count masks where breathability has at least one entry with breathability_pascals
      # that can be interpreted as a float
      Mask.all.count do |mask|
        next false if mask.breathability.blank?
        next false unless mask.breathability.is_a?(Array)

        mask.breathability.any? do |entry|
          next false unless entry.is_a?(Hash)
          next false if entry['breathability_pascals'].blank?

          # Check if it can be interpreted as a float
          begin
            Float(entry['breathability_pascals'])
            true
          rescue ArgumentError, TypeError
            false
          end
        end
      end
    end

    def fit_test_stats
      # Get all fit tests with facial measurements
      fit_tests_data = FitTestsWithFacialMeasurementsService.call

      total_fit_tests = FitTest.count

      # Count users with facial measurements
      facial_measurement_stats = calculate_facial_measurement_stats(fit_tests_data)

      # Count fit tests missing facial measurements
      fit_tests_missing_fm = FitTest.where(facial_measurement_id: nil).count

      # Calculate pass rates
      pass_rates = calculate_pass_rates(fit_tests_data)

      {
        total: total_fit_tests,
        facial_measurements: facial_measurement_stats,
        missing_facial_measurements: fit_tests_missing_fm,
        pass_rates: pass_rates
      }
    end

    def calculate_facial_measurement_stats(fit_tests_data)
      # Get unique users with fit tests
      user_ids_with_fit_tests = fit_tests_data.map { |ft| ft['user_id'] }.compact.uniq

      # Load facial measurements for these users
      facial_measurements = FacialMeasurement.where(user_id: user_ids_with_fit_tests)

      # Old set columns
      old_columns = %w[
        face_width
        face_length
        bitragion_subnasale_arc
        nasal_root_breadth
        nose_protrusion
        nose_bridge_height
      ]

      users_with_old = 0
      users_with_new = 0
      users_with_both = 0

      user_ids_with_fit_tests.each do |user_id|
        user_measurements = facial_measurements.select { |fm| fm.user_id == user_id }
        next if user_measurements.empty?

        # Check if user has all old measurements
        has_old = user_measurements.any? do |fm|
          old_columns.all? { |col| fm.send(col).present? }
        end

        # Check if user has arkit measurements
        has_new = user_measurements.any? { |fm| fm.arkit.present? }

        if has_old && has_new
          users_with_both += 1
        elsif has_old
          users_with_old += 1
        elsif has_new
          users_with_new += 1
        end
      end

      {
        users_with_old_measurements: users_with_old,
        users_with_new_measurements: users_with_new,
        users_with_both: users_with_both
      }
    end

    def calculate_pass_rates(fit_tests_data)
      # Filter out fit tests without qlft_pass data
      fit_tests_with_pass_data = fit_tests_data.reject { |ft| ft['qlft_pass'].nil? }

      Rails.logger.info "Dashboard: Total fit tests with pass data: #{fit_tests_with_pass_data.count}"
      Rails.logger.info "Dashboard: Sample fit test data keys: #{fit_tests_with_pass_data.first&.keys&.inspect}"

      # Overall pass rate
      total_with_pass_data = fit_tests_with_pass_data.count
      total_passed = fit_tests_with_pass_data.count { |ft| [true, 't'].include?(ft['qlft_pass']) }
      overall_pass_rate = total_with_pass_data.positive? ? (total_passed.to_f / total_with_pass_data * 100).round(2) : 0

      # Pass rates by mask
      by_mask = calculate_pass_rate_by_attribute(fit_tests_with_pass_data, 'mask_id', 'unique_internal_model_code')
      Rails.logger.info "Dashboard: Pass rates by mask count: #{by_mask.count}"

      # Pass rates by strap type
      by_strap_type = calculate_pass_rate_by_attribute(fit_tests_with_pass_data, 'strap_type', 'strap_type')
      Rails.logger.info "Dashboard: Pass rates by strap type count: #{by_strap_type.count}"

      # Pass rates by style
      by_style = calculate_pass_rate_by_attribute(fit_tests_with_pass_data, 'style', 'style')
      Rails.logger.info "Dashboard: Pass rates by style count: #{by_style.count}"

      {
        overall: {
          total: total_with_pass_data,
          passed: total_passed,
          pass_rate: overall_pass_rate
        },
        by_mask: by_mask,
        by_strap_type: by_strap_type,
        by_style: by_style
      }
    end

    def calculate_pass_rate_by_attribute(fit_tests_data, group_key, display_key)
      grouped = fit_tests_data.group_by { |ft| ft[group_key] }

      result = grouped.map do |key, tests|
        next if key.nil?

        total = tests.count
        passed = tests.count { |ft| [true, 't'].include?(ft['qlft_pass']) }
        pass_rate = total.positive? ? (passed.to_f / total * 100).round(2) : 0

        {
          'name' => tests.first[display_key] || key.to_s,
          'total' => total,
          'passed' => passed,
          'pass_rate' => pass_rate
        }
      end.compact.sort_by { |item| -item['pass_rate'] }

      Rails.logger.info "Dashboard: calculate_pass_rate_by_attribute for #{group_key}: #{result.inspect}"
      result
    end
  end
end
