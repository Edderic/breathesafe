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

      # Calculate fit test type breakdown
      fit_test_types = calculate_fit_test_types(fit_tests_data)

      # Calculate demographics
      demographics = calculate_demographics(fit_tests_data)

      # Calculate pass rates
      pass_rates = calculate_pass_rates(fit_tests_data)

      unique_count = fit_tests_data.map { |ft| ft['id'] }.compact.uniq.count
      unique_user_mask_pairs = fit_tests_data.map { |ft| [ft['user_id'], ft['mask_id']] }.uniq.count

      {
        total: total_fit_tests,
        total_unique: unique_count,
        unique_user_mask_pairs: unique_user_mask_pairs,
        facial_measurements: facial_measurement_stats,
        missing_facial_measurements: fit_tests_missing_fm,
        by_type: fit_test_types,
        demographics: demographics,
        pass_rates: pass_rates
      }
    end

    def calculate_fit_test_types(fit_tests_data)
      # Count fit tests by source/type
      # The 'source' field indicates which service provided the data
      type_counts = fit_tests_data.group_by { |ft| ft['source'] }.transform_values(&:count)

      # Map service names to user-friendly names
      {
        'n95_mode' => type_counts['N95ModeService'] || 0,
        'n99_mode' => type_counts['N99ModeToN95ModeConverterService'] || 0,
        'qlft' => type_counts['QlftService'] || 0,
        'user_seal_check' => type_counts['UserSealCheckFacialMeasurementsService'] || 0
      }
    end

    def calculate_demographics(fit_tests_data)
      # Get unique user IDs from fit tests
      user_ids = fit_tests_data.map { |ft| ft['user_id'] }.compact.uniq

      # Get profiles for these users
      profiles = Profile.where(user_id: user_ids)

      # Calculate gender and sex breakdown
      gender_stats = calculate_demographic_breakdown(
        fit_tests_data,
        profiles,
        'gender_and_sex',
        'Gender & Sex'
      )

      # Calculate race and ethnicity breakdown
      race_stats = calculate_demographic_breakdown(
        fit_tests_data,
        profiles,
        'race_ethnicity',
        'Race & Ethnicity'
      )

      # Calculate age breakdown
      age_stats = calculate_age_breakdown(fit_tests_data, profiles)

      {
        'gender_and_sex' => gender_stats,
        'race_ethnicity' => race_stats,
        'age' => age_stats
      }
    end

    def calculate_demographic_breakdown(fit_tests_data, profiles, field_name, _label)
      # Group fit tests by user
      fit_tests_by_user = fit_tests_data.group_by { |ft| ft['user_id'] }

      # Count fit tests and unique users by demographic value
      demographic_counts = {}

      profiles.each do |profile|
        value = profile.send(field_name)
        value = 'Prefer not to say' if value.blank?

        demographic_counts[value] ||= { fit_tests: 0, unique_users: 0 }
        demographic_counts[value][:unique_users] += 1
        demographic_counts[value][:fit_tests] += fit_tests_by_user[profile.user_id]&.count || 0
      end

      # Handle users without profiles
      users_without_profile = fit_tests_by_user.keys - profiles.map(&:user_id)
      if users_without_profile.any?
        demographic_counts['Prefer not to say'] ||= { fit_tests: 0, unique_users: 0 }
        demographic_counts['Prefer not to say'][:unique_users] += users_without_profile.count
        users_without_profile.each do |user_id|
          demographic_counts['Prefer not to say'][:fit_tests] += fit_tests_by_user[user_id]&.count || 0
        end
      end

      # Combine groups with less than 5 individuals into "Prefer not to say"
      small_groups = demographic_counts.select { |k, v| v[:unique_users] < 5 && k != 'Prefer not to say' }
      if small_groups.any?
        demographic_counts['Prefer not to say'] ||= { fit_tests: 0, unique_users: 0 }
        small_groups.each do |key, counts|
          demographic_counts['Prefer not to say'][:fit_tests] += counts[:fit_tests]
          demographic_counts['Prefer not to say'][:unique_users] += counts[:unique_users]
          demographic_counts.delete(key)
        end
      end

      # Convert to array format for frontend
      result = demographic_counts.map do |value, counts|
        {
          'name' => value,
          'fit_tests' => counts[:fit_tests],
          'unique_users' => counts[:unique_users]
        }
      end

      result.sort_by { |item| -item['fit_tests'] }
    end

    def calculate_age_breakdown(fit_tests_data, profiles)
      # Group fit tests by user
      fit_tests_by_user = fit_tests_data.group_by { |ft| ft['user_id'] }

      # Define age ranges
      current_year = Time.current.year
      age_ranges = [
        { label: '18-25', min: current_year - 25, max: current_year - 18 },
        { label: '26-35', min: current_year - 35, max: current_year - 26 },
        { label: '36-45', min: current_year - 45, max: current_year - 36 },
        { label: '46-55', min: current_year - 55, max: current_year - 46 },
        { label: '56-65', min: current_year - 65, max: current_year - 56 },
        { label: '66+', min: 0, max: current_year - 66 }
      ]

      # Count fit tests and unique users by age range
      age_counts = {}
      age_ranges.each { |range| age_counts[range[:label]] = { fit_tests: 0, unique_users: 0 } }
      age_counts['Prefer not to say'] = { fit_tests: 0, unique_users: 0 }

      profiles.each do |profile|
        year_of_birth = profile.year_of_birth

        if year_of_birth.blank?
          age_counts['Prefer not to say'][:unique_users] += 1
          age_counts['Prefer not to say'][:fit_tests] += fit_tests_by_user[profile.user_id]&.count || 0
          next
        end

        # Find matching age range
        age_range = age_ranges.find do |range|
          if range[:label] == '66+'
            year_of_birth.to_i <= range[:max]
          else
            year_of_birth.to_i >= range[:min] && year_of_birth.to_i <= range[:max]
          end
        end

        if age_range
          age_counts[age_range[:label]][:unique_users] += 1
          age_counts[age_range[:label]][:fit_tests] += fit_tests_by_user[profile.user_id]&.count || 0
        else
          age_counts['Prefer not to say'][:unique_users] += 1
          age_counts['Prefer not to say'][:fit_tests] += fit_tests_by_user[profile.user_id]&.count || 0
        end
      end

      # Handle users without profiles
      users_without_profile = fit_tests_by_user.keys - profiles.map(&:user_id)
      if users_without_profile.any?
        age_counts['Prefer not to say'][:unique_users] += users_without_profile.count
        users_without_profile.each do |user_id|
          age_counts['Prefer not to say'][:fit_tests] += fit_tests_by_user[user_id]&.count || 0
        end
      end

      # Combine groups with less than 5 individuals into "Prefer not to say"
      small_groups = age_counts.select { |k, v| v[:unique_users] < 5 && k != 'Prefer not to say' }
      if small_groups.any?
        small_groups.each do |key, counts|
          age_counts['Prefer not to say'][:fit_tests] += counts[:fit_tests]
          age_counts['Prefer not to say'][:unique_users] += counts[:unique_users]
          age_counts.delete(key)
        end
      end

      # Convert to array format for frontend, maintaining age range order
      result = []
      age_ranges.each do |range|
        next unless age_counts[range[:label]]

        result << {
          'name' => range[:label],
          'fit_tests' => age_counts[range[:label]][:fit_tests],
          'unique_users' => age_counts[range[:label]][:unique_users]
        }
      end

      # Add "Prefer not to say" at the end
      prefer_not_to_say = age_counts['Prefer not to say']
      if prefer_not_to_say[:fit_tests].positive? || prefer_not_to_say[:unique_users].positive?
        result << {
          'name' => 'Prefer not to say',
          'fit_tests' => prefer_not_to_say[:fit_tests],
          'unique_users' => prefer_not_to_say[:unique_users]
        }
      end

      result
    end

    def calculate_facial_measurement_stats(fit_tests_data)
      # Get unique users with fit tests
      user_ids_with_fit_tests = fit_tests_data.map { |ft| ft['user_id'] }.compact.uniq

      # Load facial measurements for these users
      facial_measurements = FacialMeasurement.where(user_id: user_ids_with_fit_tests)

      # Traditional measurement columns
      traditional_columns = %w[
        face_width
        face_length
        bitragion_subnasale_arc
        nasal_root_breadth
        nose_protrusion
        nose_bridge_height
      ]

      # Initialize counters (non-mutually exclusive)
      users_with_incomplete_traditional = 0
      users_with_complete_traditional = 0
      users_with_arkit = 0
      users_with_both_complete = 0
      users_with_no_measurements = 0

      user_ids_with_fit_tests.each do |user_id|
        user_measurements = facial_measurements.select { |fm| fm.user_id == user_id }

        # Check if user has complete traditional measurements (all 6)
        has_complete_traditional = user_measurements.any? do |fm|
          traditional_columns.all? { |col| fm.send(col).present? }
        end

        # Check if user has any traditional measurements (1-6)
        has_any_traditional = user_measurements.any? do |fm|
          traditional_columns.any? { |col| fm.send(col).present? }
        end

        # Check if user has incomplete traditional (has some but not all)
        has_incomplete_traditional = has_any_traditional && !has_complete_traditional

        # Check if user has ARKit measurements
        has_arkit = user_measurements.any? { |fm| fm.arkit.present? }

        # Check if user has no measurements at all
        has_no_measurements = !has_any_traditional && !has_arkit

        # Count in each applicable category (non-mutually exclusive)
        users_with_incomplete_traditional += 1 if has_incomplete_traditional || (!has_any_traditional && !has_arkit)
        users_with_complete_traditional += 1 if has_complete_traditional
        users_with_arkit += 1 if has_arkit
        users_with_both_complete += 1 if has_complete_traditional && has_arkit
        users_with_no_measurements += 1 if has_no_measurements
      end

      {
        users_with_incomplete_traditional: users_with_incomplete_traditional,
        users_with_complete_traditional: users_with_complete_traditional,
        users_with_arkit: users_with_arkit,
        users_with_both_complete: users_with_both_complete,
        users_with_no_measurements: users_with_no_measurements
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
      end
      result = result.compact
      result = result.sort_by { |item| -item['pass_rate'] }

      Rails.logger.info "Dashboard: calculate_pass_rate_by_attribute for #{group_key}: #{result.inspect}"
      result
    end
  end
end
