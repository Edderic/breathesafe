# frozen_string_literal: true

# Hits the Mask Recommender endpoint with facial measurement data,
# gets list of masks with probability of fit estimates.
class MaskRecommenderController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    status = 200
    # Prefer explicit function_base param (nested or top-level)
    function_base = params[:function_base] || params.dig(:mask_recommender, :function_base) || 'mask-recommender'
    masks = MaskRecommender.infer(facial_measurements.to_h.stringify_keys, function_base: function_base)
    data_context = MasksDataContextualizer.call

    respond_to do |format|
      format.json do
        render json: { masks: masks, context: data_context }.to_json, status: status
      end
    end
  end

  def create_async
    function_base = params[:function_base] || params.dig(:mask_recommender, :function_base) || 'mask-recommender'
    job_id = SecureRandom.uuid
    cache_key = MaskRecommenderJob.cache_key(job_id)
    Rails.cache.write(
      cache_key,
      { status: 'queued', created_at: Time.current.iso8601 },
      expires_in: MaskRecommenderJob::CACHE_TTL
    )

    begin
      MaskRecommenderJob.perform_later(
        job_id: job_id,
        facial_measurements: facial_measurements.to_h.stringify_keys,
        function_base: function_base
      )
    rescue RedisClient::CannotConnectError => e
      Rails.cache.delete(cache_key)
      render json: { error: e.message }, status: :service_unavailable
      return
    end

    render json: { job_id: job_id, status: 'queued' }, status: :accepted
  end

  def train
    unless current_user&.admin
      render json: { error: 'forbidden' }, status: :forbidden
      return
    end

    job_id = SecureRandom.uuid
    payload = {
      environment: ENV.fetch('HEROKU_ENVIRONMENT', 'development'),
      job_id: job_id
    }
    result = MaskRecommenderTraining.call(payload: payload)
    render json: { job_id: job_id, status: 'started', result: result }, status: :ok
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def status
    job_id = params[:id].to_s
    payload = Rails.cache.read(MaskRecommenderJob.cache_key(job_id))

    if payload.blank?
      render json: { error: 'not_found' }, status: :not_found
      return
    end

    if payload[:status] == 'complete'
      render json: payload, status: :ok
    else
      render json: payload.except(:result), status: :ok
    end
  end

  def facial_measurements
    params.require(:facial_measurements).permit(
      *FacialMeasurement::RECOMMENDER_COLUMNS.map(&:to_sym),
      :facial_hair_beard_length_mm
    )
  end

  def recommender_columns
    render json: { recommender_columns: FacialMeasurement::RECOMMENDER_COLUMNS }
  end
end
