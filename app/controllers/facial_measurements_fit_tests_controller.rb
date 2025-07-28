# frozen_string_literal: true

class FacialMeasurementsFitTestsController < ApplicationController
  before_action :authenticate_user!, only: [:create]

  def create
    # TODO: what happens when the facial measurement id is invalid?
    # Will want to return
    fm = FacialMeasurement.find_by(id: facial_measurement_id)

    if fm.nil?
      status = 401
      messages = ['No facial measurement found for this id.']
    elsif unauthorized?
      status = 401
      messages = ['Unauthorized.']
    else
      user = fm.user

      if current_user.manages?(user)
        # assumes that facial measurements have user ids always
        fit_tests = FitTest.where(user_id: fm.user_id)

        ApplicationRecord.transaction do
          fit_tests.each do |ft|
            ft.update(facial_measurement_id: fm.id)
          end
        end

        status = 201
        messages = ['Successfully assigned latest facial measurement to past fit tests.']
      else
        status = 401
        messages = ['Unauthorized.']
      end
    end

    to_render = {
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def index
    fit_tests_with_facial_measurements = FitTestsWithFacialMeasurementsService.call

    to_render = {
      fit_tests_with_facial_measurements: fit_tests_with_facial_measurements
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: :ok
      end
    end
  end

  def show
    fit_tests_with_facial_measurements = \
      FitTestsWithFacialMeasurementsService.call(mask_id: mask_id)

    to_render = {
      fit_tests_with_facial_measurements: fit_tests_with_facial_measurements
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: :ok
      end
    end
  end

  private

  def facial_measurement_id
    params[:facial_measurement_id].to_i
  end

  def mask_id
    params[:mask_id]
  end
end
