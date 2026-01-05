# frozen_string_literal: true

class FitTestsWithFacialMeasurementsService
  class << self
    def call(mask_id: nil, with_demographics: false, exclude_nil_pass: true, include_without_facial_measurements: false)
      n95_mode_experimental_scores = N95ModeService.call(mask_id: mask_id).to_a
      n95_mode_estimate_scores_from_n99 = N99ModeToN95ModeConverterService.call(mask_id: mask_id).to_a
      # If each exercise that is NOT NULL is passed, then qlft_score for that
      # fit test will be a pass.
      qlft_scores = QlftService.call(mask_id: mask_id).to_a
      user_seal_check_scores = UserSealCheckFacialMeasurementsService.call(mask_id: mask_id).to_a

      results = n95_mode_experimental_scores | n95_mode_estimate_scores_from_n99 | qlft_scores | user_seal_check_scores

      results = results.reject { |r| r['qlft_pass'].nil? } if exclude_nil_pass
      results = results.select { |r| r['facial_measurement_id'].present? } unless include_without_facial_measurements

      # Add demographics if requested
      results = add_demographics(results) if with_demographics

      results

      # For most people, if user seal check failed, then we assume QLFT fails.
      # And they would not include data for QLFT, N95 mode, N99 mode
      # There will generally be only one QLFT entry per user-mask combo.
      #
      # Exceptions are my case where I'm collecting both N99 mode, N95 mode,
      # QLFT, and User Seal Check
      #
      # There could be cases where
      #
      # User Seal Check | QLFT | N95 mode | N99 mode |
      #      F          |      |          |          |
      #      P          |      |          |          |
      #      P          |      |          |          |
    end

    private

    def add_demographics(results)
      # Get unique user_ids to batch load profiles
      user_ids = results.map { |r| r['user_id'] }.compact.uniq
      profiles_by_user_id = Profile.where(user_id: user_ids).index_by(&:user_id)

      results.map do |result|
        user_id = result['user_id']
        profile = profiles_by_user_id[user_id]
        created_at = result['created_at']

        # Add race_ethnicity
        result['race_ethnicity'] = if profile && profile.race_ethnicity.present?
                                     profile.race_ethnicity
                                   else
                                     'Prefer not to disclose'
                                   end

        # Add gender_and_sex
        result['gender_and_sex'] = if profile && profile.gender_and_sex.present?
                                     profile.gender_and_sex
                                   else
                                     'Prefer not to disclose'
                                   end

        # Calculate and add age bracket
        result['age_bracket'] = calculate_age_bracket(profile, created_at)

        result
      end
    end

    def calculate_age_bracket(profile, created_at)
      # Return 'blank' if year_of_birth is not present (prefer not to disclose)
      return 'blank' unless profile && profile.year_of_birth.present?

      # Return 'blank' if created_at is missing
      return 'blank' unless created_at

      # Parse created_at - handle various formats (Time, DateTime, String, Date)
      fit_test_year = if created_at.respond_to?(:year)
                        created_at.year
                      elsif created_at.is_a?(String)
                        # Try to parse as date/time (handles PostgreSQL timestamps)
                        begin
                          parsed_date = DateTime.parse(created_at)
                          parsed_date.year
                        rescue StandardError
                          # If parsing fails, try extracting year from string
                          # (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
                          year_match = created_at.match(/^(\d{4})/)
                          year_match ? year_match[1].to_i : nil
                        end
                      else
                        # Fallback: try to convert to string and extract year
                        year_match = created_at.to_s.match(/^(\d{4})/)
                        year_match ? year_match[1].to_i : nil
                      end

      return 'blank' unless fit_test_year

      year_of_birth = profile.year_of_birth.to_i
      age = fit_test_year - year_of_birth

      # Handle edge cases
      return 'blank' if age.negative? # Invalid age (future birth year)

      case age
      when 0...2
        '0-2'
      when 2...4
        '2-4'
      when 4...6
        '4-6'
      when 6...8
        '6-8'
      when 8...10
        '8-10'
      when 10...12
        '10-12'
      when 12...14
        '12-14'
      when 14...18
        '14-18'
      when 18..Float::INFINITY
        'age_adult'
      else
        'blank'
      end
    end
  end
end
