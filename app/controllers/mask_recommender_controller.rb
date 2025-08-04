# frozen_string_literal: true

# Hits the Mask Recommender endpoint with facial measurement data,
# gets list of masks with probability of fit estimates.
class MaskRecommenderController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    status = 200
    masks = MaskRecommender.call(facial_measurements)

    respond_to do |format|
      format.json do
        render json: masks.to_json, status: status
      end
    end
  end

  def facial_measurements
    params.require(:facial_measurements).permit(
      :bitragion_subnasale_arc,
      :face_width,
      :nose_protrusion,
      :facial_hair_beard_length_mm
    )
  end
end
