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

      # Ensure results has proper structure if not provided or empty
      fit_test_params = fit_test_data.merge(
        facial_measurement_id: fm_id,
        user_id: user.id
      )

      # Set default results structure if missing or empty
      if fit_test_params[:results].blank?
        fit_test_params[:results] = {
          'qualitative' => {
            'aerosol' => { 'solution' => 'Saccharin' },
            'exercises' => [
              { 'name' => 'Normal breathing', 'result' => nil },
              { 'name' => 'Deep breathing', 'result' => nil },
              { 'name' => 'Turning head side to side', 'result' => nil },
              { 'name' => 'Moving head up and down', 'result' => nil },
              { 'name' => 'Talking', 'result' => nil },
              { 'name' => 'Bending over', 'result' => nil },
              { 'name' => 'Normal breathing', 'result' => nil }
            ],
            'procedure' => nil
          },
          'quantitative' => {
            'exercises' => [
              { 'name' => 'Bending over', 'fit_factor' => nil },
              { 'name' => 'Talking', 'fit_factor' => nil },
              { 'name' => 'Turning head side to side', 'fit_factor' => nil },
              { 'name' => 'Moving head up and down', 'fit_factor' => nil },
              { 'name' => 'Normal breathing 1', 'fit_factor' => nil },
              { 'name' => 'Normal breathing 2', 'fit_factor' => nil },
              { 'name' => 'Grimace', 'fit_factor' => nil },
              { 'name' => 'Deep breathing', 'fit_factor' => nil },
              { 'name' => 'Normal breathing (SEALED)', 'fit_factor' => nil }
            ],
            'testing_mode' => 'N95'
          }
        }
      end

      fit_test = FitTest.create(fit_test_params)

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
    start_time = Time.current
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      fit_tests = []
      tested_and_untested = []
    else
      viewable_start = Time.current
      fit_tests_json = FitTest.viewable(current_user).to_json
      Rails.logger.debug "FitTest.viewable + to_json took: #{(Time.current - viewable_start) * 1000}ms"

      parse_start = Time.current
      fit_tests = JSON.parse(fit_tests_json)
      Rails.logger.debug "JSON.parse took: #{(Time.current - parse_start) * 1000}ms"

      messages = []

      mask_kit_start = Time.current
      tested_and_untested = MaskKitQuery.managed_by(manager_id: current_user.id)
      Rails.logger.debug "MaskKitQuery.managed_by took: #{(Time.current - mask_kit_start) * 1000}ms"
    end

    Rails.logger.debug "FitTestsController#index total time: #{(Time.current - start_time) * 1000}ms"

    render_start = Time.current
    to_render = {
      fit_tests: fit_tests,
      tested_and_untested: tested_and_untested,
      messages: messages
    }

    respond_to do |format|
      format.json do
        json_render_start = Time.current
        json_output = to_render.to_json
        Rails.logger.debug "FitTestsController#index: to_json took: #{(Time.current - json_render_start) * 1000}ms"
        render json: json_output, status: status
      end
    end
    Rails.logger.debug "FitTestsController#index: Render preparation took: #{(Time.current - render_start) * 1000}ms"
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

    if fit_test.destroy
      status = 200
      messages = []
    else
      status = 422
      messages = fit_test.errors.full_messages
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

  def clone
    original_fit_test = FitTest.find(params[:id])
    user = original_fit_test.user

    # Get latest facial measurement
    latest_facial_measurement = FacialMeasurement.latest(user)
    fm_id = latest_facial_measurement&.id

    # Clone all attributes except id, created_at, updated_at
    cloned_attributes = original_fit_test.attributes.except('id', 'created_at', 'updated_at')
    cloned_attributes['facial_measurement_id'] = fm_id
    cloned_attributes['user_id'] = user.id

    # Remove any nil values that might cause issues
    cloned_attributes = cloned_attributes.compact

    fit_test = FitTest.create(cloned_attributes)

    if fit_test.persisted?
      status = 201
      messages = []
      to_render = {
        fit_test: JSON.parse(fit_test.to_json),
        messages: messages
      }
    else
      status = 422
      messages = fit_test.errors.full_messages
      to_render = {
        messages: messages
      }
    end

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
      :mask_modded,
      :notes,
      :procedure,
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
