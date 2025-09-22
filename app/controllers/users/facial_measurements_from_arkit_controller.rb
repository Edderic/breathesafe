# frozen_string_literal: true

module Users
  # Controller for facial measurements from ARKit
  class FacialMeasurementsFromArkitController < ApplicationController
    skip_before_action :verify_authenticity_token

    def create
      for_user = User.find(params[:user_id])

      if unauthorized?
        status = 401
        messages = ['Unauthorized.']
        facial_measurement = {}

      elsif !current_user.manages?(for_user)
        status = 422
        messages = ['Not managed by current user.']
        facial_measurement = {}

      else
        # Create facial measurement with ARKit data
        facial_measurement = FacialMeasurement.create(
          user_id: for_user.id,
          source: 'arkit',
          arkit: arkit_payload
        )

        if facial_measurement.errors.full_messages.size.positive?
          status = 422
          messages = facial_measurement.errors.full_messages
        else
          status = 201
          messages = []
        end
      end

      to_render = {
        facial_measurement: facial_measurement,
        messages: messages
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: status
        end
      end
    end

    private

    def arkit_payload
      params.require(:arkit_data)
    end
  end
end