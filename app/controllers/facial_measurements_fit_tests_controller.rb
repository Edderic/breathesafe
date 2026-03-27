# frozen_string_literal: true

# Controller featuring CRUD operations for Facial Measurements and Fit Tests
class FacialMeasurementsFitTestsController < ApplicationController
  before_action :authenticate_user!, only: [:create]
  before_action :authorize_dataset_access!, only: %i[index show]

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
    if with_demographics && internal_export_request?
      to_render = {
        fit_tests_with_facial_measurements: [],
        messages: ['Unauthorized. Internal export does not allow demographics.']
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: :forbidden
        end
      end
      return
    end

    if with_demographics && !current_user.admin
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
    if with_demographics && internal_export_request?
      to_render = {
        fit_tests_with_facial_measurements: [],
        messages: ['Unauthorized. Internal export does not allow demographics.']
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: :forbidden
        end
      end
      return
    end

    if with_demographics && !current_user.admin
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

  def authorize_dataset_access!
    return if internal_export_authorized?

    if unauthorized?
      render json: { fit_tests_with_facial_measurements: [], messages: ['Unauthorized.'] }, status: :unauthorized
      return
    end

    return if current_user.admin

    render json: {
      fit_tests_with_facial_measurements: [],
      messages: ['Unauthorized. Admin access required.']
    }, status: :forbidden
  end

  def internal_export_request?
    ActiveModel::Type::Boolean.new.cast(params[:internal_export])
  end

  def internal_export_authorized?
    return false unless internal_export_request?

    token = internal_export_token
    provided_token = request.headers['X-Breathesafe-Internal-Token'].to_s
    return false if token.blank? || provided_token.blank?

    ActiveSupport::SecurityUtils.secure_compare(provided_token, token)
  end

  def internal_export_token
    ENV['MASK_RECOMMENDER_INTERNAL_API_TOKEN'].to_s
  end
end
