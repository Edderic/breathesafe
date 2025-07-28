# frozen_string_literal: true

class FitTestsWithFacialMeasurementsService
  class << self
    def call(mask_id: nil)
      n95_mode_experimental_scores = N95ModeService.call(mask_id: mask_id).to_a
      n95_mode_estimate_scores_from_n99 = N99ModeToN95ModeConverterService.call(mask_id: mask_id).to_a
      qlft_scores = QlftService.call(mask_id: mask_id).to_a
      user_seal_check_scores = UserSealCheckFacialMeasurementsService.call(mask_id: mask_id).to_a

      results = n95_mode_experimental_scores | n95_mode_estimate_scores_from_n99 | qlft_scores | user_seal_check_scores

      results.reject { |r| r['qlft_pass'].nil? }

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
  end
end
