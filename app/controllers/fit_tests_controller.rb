# frozen_string_literal: true

# CRUD for Fit Testing data
class FitTestsController < ApplicationController
  def create
    fit_test = {}
    user = User.find(user_data[:id])

    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
    elsif !current_user.manages?(user)
      status = 422
      messages = ['Unauthorized.']
    else
      # assumes there is facial measurement information
      latest_facial_measurement = FacialMeasurement.latest(user)

      fm_id = nil

      fm_id = latest_facial_measurement.id if latest_facial_measurement

      fit_test = FitTest.create(
        fit_test_data.merge(
          facial_measurement_id: fm_id,
          user_id: user.id
        )
      )

      if fit_test
        status = 201
        messages = []
      else
        status = 422
        messages = fit_test.errors.full_messages
        fit_test = {}
      end
    end

    to_render = {
      fit_test: fit_test,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def index
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      fit_tests = []
      tested_and_untested = []
    else
      fit_tests = JSON.parse(
        FitTest.viewable(current_user).to_json
      )
      messages = []
      tested_and_untested = MaskKitQuery.managed_by(manager_id: current_user.id)
    end

    to_render = {
      fit_tests: fit_tests,
      tested_and_untested: tested_and_untested,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def show
    fit_test = FitTest.find(params[:id])
    to_render = {}
    messages = []

    if !current_user
      status = 401
      ['Unauthorized.']

    elsif !current_user.manages?(fit_test_user)
      ['Unauthorized.']
    else
      to_render = {
        fit_test: JSON.parse(fit_test.to_json),
        messages: messages
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def update
    fit_test = FitTest.find(params[:id])

    if !current_user
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    elsif !current_user.manages?(fit_test_user)
      status = 401
      messages = ['Unauthorized.']
    elsif fit_test.update(fit_test_data)
      status = 204
      messages = []
    else
      status = 400 # bad request
      messages = []
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

  def delete
    fit_test = FitTest.find(params[:id])

    if !current_user
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    elsif !current_user.manages?(fit_test_user)
      status = 401
      messages = ['Unauthorized.']
    elsif fit_test.delete
      status = 200
      messages = []
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

  def fit_test_data
    params.require(:fit_test).permit(
      :fit_test_id,
      :mask_id,
      :quantitative_fit_testing_device_id,
      facial_hair: %w[
        beard_length_mm
        beard_cover_technique
      ],
      results: [
        quantitative: [
          'procedure',
          'testing_mode',
          'notes',
          { aerosol: %i[
              solution
              initial_count_per_cm3
            ],
            exercises: %w[
              name
              fit_factor
            ] }
        ],
        qualitative: [
          'procedure',
          'notes',
          { aerosol: [
              :solution
            ],
            exercises: %w[
              name
              result
            ] }
        ]
      ],
      user_seal_check: [
        'positive': [
          '...how much air movement on your face along the seal of the mask did you feel?',
          '...how much did your glasses fog up?',
          '...how much pressure build up was there?'
        ],
        'negative': [
          '...how much air passed between your face and the mask?'
        ],
        'sizing': [
          'What do you think about the sizing of this mask relative to your face?'
        ]
      ],
      comfort: [
        'How comfortable is the position of the mask on the nose?',
        'Is there adequate room for eye protection?',
        'Is there enough room to talk?',
        'How comfortable is the position of the mask on face and cheeks?'
      ]
    )
  end

  def user_data
    params.require(:user).permit(:id)
  end

  def fit_test_user
    fit_test = FitTest.find(params[:id])
    fit_test.user
  end
end
