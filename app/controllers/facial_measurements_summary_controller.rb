# frozen_string_literal: true

# Exposes a combined view of traditional and ARKit facial measurements per user.
class FacialMeasurementsSummaryController < ApplicationController
  def index
    if unauthorized?
      render json: { messages: ['Unauthorized.'] }, status: :unauthorized
      return
    end

    data = FacialMeasurementsService.call

    render json: {
      facial_measurements: data
    }, status: :ok
  end
end
