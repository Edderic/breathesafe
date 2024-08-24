class FitTestsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    if unauthorized?
      status = 401
      message = "Unauthorized."
      fit_test = {}
    else
      latest_facial_measurement = FacialMeasurement.latest(current_user)

      unless latest_facial_measurement
        status = 422
        message = "No facial measurements added yet. Please add facial measurements before adding a fit test."
      else
        fit_test = FitTest.create(
          fit_test_data.merge(
            facial_measurement_id: latest_facial_measurement.id,
          )
        )

        if fit_test
          status = 201
          message = ""
        else
          status = 422
          message = "FitTest creation failed."
          fit_test = {}
        end
      end
    end

    to_render = {
      fit_test: fit_test,
      message: message
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def index
    # TODO: should only be scoped to the current user
    # TODO: if admin, could see all, with name?
    to_render = {
      fit_tests: JSON.parse(
        FitTest.viewable(current_user).to_json
      )
    }
    message = ""

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      message = "Unauthorized."
      to_render = {}
    else
      to_render = {
        fit_test: JSON.parse(FitTest.find(params[:id]).to_json)
      }
    end


    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def update
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      message = "Unauthorized."
      to_render = {}
    end

    fit_test = FitTest.find(params[:id])

    # TODO: admins should be able to update data no matter who owns it.
    if fit_test.facial_measurement.user_id != current_user.id
      status = 401
      to_render = {}
      message = 'Unauthorized.'
    elsif fit_test.update(fit_test_data)
      status = 204
      to_render = {}
      message = ""
    else
      status = 400 # bad request
      to_render = {}
      message = ""
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def delete
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      message = "Unauthorized."
      to_render = {}
    end

    fit_test = FitTest.find(params[:id])


    # TODO: admins should be able to update data no matter who owns it.
    if !fit_test.author_ids.include?(current_user.id)
      status = 401
      to_render = {}
      message = 'Unauthorized.'
    elsif fit_test.delete
      status = 200
      to_render = {}
      message = ""
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, message: message
      end
    end
  end

  def fit_test_data
    params.require(:fit_test).permit(
      :fit_test_id,
      :mask_id,
      facial_hair: [
        :beard_length_mm,
        :beard_cover_technique
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
end


