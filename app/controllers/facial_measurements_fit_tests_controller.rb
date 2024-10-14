class FacialMeasurementsFitTestsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    # TODO: what happens when the facial measurement id is invalid?
    # Will want to return
    fm = FacialMeasurement.find_by(id: facial_measurement_id)

    if fm.nil?
      status = 401
      messages = ["No facial measurement found for this id."]
    elsif unauthorized?
      status = 401
      messages = ["Unauthorized."]
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
        messages = ["Successfully assigned latest facial measurement to past fit tests."]
      else
        status = 401
        messages = ["Unauthorized."]
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
  end

  private

  def facial_measurement_id
    params[:facial_measurement_id]
  end
end
