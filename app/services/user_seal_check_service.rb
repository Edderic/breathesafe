# frozen_string_literal: true

class UserSealCheckService
  class << self
    # Evaluates a user seal check hash and returns 'pass', 'fail', or 'incomplete'
    #
    # @param user_seal_check [Hash, String, nil] The user seal check data structure (hash or JSON string)
    # @return [String] 'pass', 'fail', or 'incomplete'
    def evaluate(user_seal_check)
      return 'incomplete' if user_seal_check.nil?

      # Parse JSON string if needed
      parsed = if user_seal_check.is_a?(String)
                 begin
                   JSON.parse(user_seal_check)
                 rescue JSON::ParserError
                   return 'incomplete'
                 end
               else
                 user_seal_check
               end

      return 'incomplete' if parsed.empty?

      sizing_question = 'What do you think about the sizing of this mask relative to your face?'
      air_movement_question = '...how much air movement on your face along the seal of the mask did you feel?'

      sizing = parsed.dig('sizing', sizing_question) || parsed.dig(:sizing, sizing_question)
      air_movement = parsed.dig('positive', air_movement_question) || parsed.dig(:positive, air_movement_question)

      # Check if sizing question is missing
      return 'incomplete' if sizing.nil? || sizing.to_s.strip.empty?

      # Check if air movement question is missing
      return 'incomplete' if air_movement.nil? || air_movement.to_s.strip.empty?

      # Fail if "Too big" or "Too small" is selected
      return 'fail' if ['Too big', 'Too small'].include?(sizing.to_s)

      # Fail if "A lot of air movement" is selected
      return 'fail' if air_movement.to_s == 'A lot of air movement'

      # Pass if "Somewhere in-between too small and too big" AND ("Some air movement" OR "No air movement")
      if (sizing.to_s == 'Somewhere in-between too small and too big') \
        && ['Some air movement', 'No air movement'].include?(air_movement.to_s)
        return 'pass'
      end

      # If we get here, the combination doesn't match our pass criteria
      # This shouldn't happen with valid data, but return incomplete as a fallback
      'incomplete'
    end

    # Evaluates user seal check for a FitTest instance
    #
    # @param fit_test [FitTest] The FitTest instance
    # @return [String] 'pass', 'fail', or 'incomplete'
    def evaluate_for_fit_test(fit_test)
      return 'incomplete' unless fit_test.respond_to?(:user_seal_check)

      evaluate(fit_test.user_seal_check)
    end

    # Determines qlft_pass value based on user seal check result
    # Returns false if user seal check fails, NULL otherwise
    #
    # @param user_seal_check [Hash, nil] The user seal check data structure
    # @return [Boolean, nil] false if failed, nil otherwise
    def qlft_pass_value(user_seal_check)
      result = evaluate(user_seal_check)
      result == 'fail' ? false : nil
    end
  end
end
