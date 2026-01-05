# frozen_string_literal: true

# Controller featuring CRUD operations for Facial Measurements and Fit Tests
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
    # Check if demographics are requested
    with_demographics = params[:with_demographics] == 'true'

    # If demographics are requested, verify admin access
    if with_demographics && (unauthorized? || !current_user.admin)
      to_render = {
        fit_tests_with_facial_measurements: [],
        messages: ['Unauthorized. Admin access required to view demographics.']
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: :forbidden
        end
      end
      return
    end

    include_without = ActiveModel::Type::Boolean.new.cast(
      params[:include_without_facial_measurements]
    )
    fit_tests_with_facial_measurements = FitTestsWithFacialMeasurementsService.call(
      with_demographics: with_demographics,
      exclude_nil_pass: false,
      include_without_facial_measurements: include_without
    )

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
    # Check if demographics are requested
    with_demographics = params[:with_demographics] == 'true'

    # If demographics are requested, verify admin access
    if with_demographics && (unauthorized? || !current_user.admin)
      to_render = {
        fit_tests_with_facial_measurements: [],
        messages: ['Unauthorized. Admin access required to view demographics.']
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: :forbidden
        end
      end
      return
    end

    include_without = ActiveModel::Type::Boolean.new.cast(
      params[:include_without_facial_measurements]
    )
    fit_tests_with_facial_measurements =
      FitTestsWithFacialMeasurementsService.call(
        mask_id: mask_id,
        with_demographics: with_demographics,
        exclude_nil_pass: false,
        include_without_facial_measurements: include_without
      )

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
