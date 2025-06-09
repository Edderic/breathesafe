class FitTestsWithFacialMeasurementsService
  class << self
    def call
      n95_mode_experimental_scores = N95ModeService.call.to_a
      n95_mode_estimate_scores_from_n99 = N99ModeToN95ModeConverterService.call.to_a
      qlft_scores = QlftService.call.to_a

      n95_mode_experimental_scores | n95_mode_estimate_scores_from_n99 | qlft_scores
    end
  end
end
