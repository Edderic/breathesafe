class FitTestsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    fit_test = {}
    user = User.find(user_data[:id])

    if unauthorized?
      status = 401
      messages = ["Unauthorized."]
    elsif !current_user.manages?(user)
      status = 422
      messages = ["Unauthorized."]
    else
      # assumes there is facial measurement information
      latest_facial_measurement = FacialMeasurement.latest(user)

      fm_id = nil

      if latest_facial_measurement
        fm_id = latest_facial_measurement.id
      end

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
      messages = ["Unauthorized."]
      fit_tests = []
    else
      fit_tests = JSON.parse(
        FitTest.viewable(current_user).to_json
      )
      messages = []
    end
    tested_and_untested = JSON.parse(Mask.find_targeted_but_untested_masks(current_user.id).to_json)

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
    fit_test = FitTest.find_by_id_with_user_id(params[:id])
    to_render = {}
    messages = []

    if !current_user
      status = 401
      messages = ["Unauthorized."]

    elsif !current_user.manages?(fit_test_user)
      messages = ["Unauthorized."]
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
      messages = ["Unauthorized."]
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
      messages = ["Unauthorized."]
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
      facial_hair: [
        'beard_length_mm',
        'beard_cover_technique'
      ],
      results: [
        quantitative: [
          'procedure',
          'testing_mode',
          'notes',
          aerosol: [
            :solution,
            :initial_count_per_cm3
          ],
          exercises: [
            'name',
            'fit_factor'
          ],
        ],
        qualitative: [
          'procedure',
          'notes',
          aerosol: [
            :solution
          ],
          exercises: [
            'name',
            'result'
          ]
        ]
      ],
      user_seal_check: [
        'positive': [
          "...how much air movement on your face along the seal of the mask did you feel?",
          '...how much did your glasses fog up?',
          '...how much pressure build up was there?'
        ],
        'negative': [
          '...how much air passed between your face and the mask?'
        ],
        'sizing': [
          "What do you think about the sizing of this mask relative to your face?"
        ]
      ],
      comfort: [
        "How comfortable is the position of the mask on the nose?",
        "Is there adequate room for eye protection?",
        "Is there enough room to talk?",
        "How comfortable is the position of the mask on face and cheeks?"
      ],
    )
  end

  def user_data
    params.require(:user).permit(:id)
  end

  def fit_test_user
    fit_test = FitTest.find(params[:id])
    return fit_test.user
  end
end


