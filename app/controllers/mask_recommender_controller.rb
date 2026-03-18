# frozen_string_literal: true

# Hits the Mask Recommender endpoint with facial measurement data,
# gets list of masks with probability of fit estimates.
class MaskRecommenderController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    status, body = build_recommendation_response

    respond_to do |format|
      format.json { render json: body.to_json, status: status }
    end
  end

  def create_async
    function_base = params[:function_base] || params.dig(:mask_recommender, :function_base) || 'mask-recommender'
    model_type = params[:model_type].presence || params.dig(:mask_recommender, :model_type).presence
    resolved_facial_measurements = resolved_facial_measurements_payload
    if resolved_facial_measurements.is_a?(Hash) && resolved_facial_measurements[:error]
      render json: { error: resolved_facial_measurements[:error] }, status: resolved_facial_measurements[:status]
      return
    end

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
        facial_measurements: resolved_facial_measurements,
        function_base: function_base,
        model_type: model_type,
        recommender_user_id: params[:recommender_user_id].presence,
        viewer_id: current_user&.id
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
    model_type = params[:model_type].presence || params.dig(:mask_recommender, :model_type).presence
    epochs = params[:epochs].presence || params.dig(:mask_recommender, :epochs).presence
    learning_rate = params[:learning_rate].presence || params.dig(:mask_recommender, :learning_rate).presence
    payload = {
      environment: ENV.fetch('HEROKU_ENVIRONMENT', 'development'),
      job_id: job_id,
      model_type: model_type,
      epochs: epochs,
      learning_rate: learning_rate
    }
    result = MaskRecommenderTraining.call(payload: payload)
    if result.is_a?(Hash) && result['statusCode'].to_i >= 400
      lambda_body = result['body'].is_a?(String) ? JSON.parse(result['body']) : result['body']
      error_message = lambda_body.is_a?(Hash) ? (lambda_body['message'] || lambda_body['error']) : nil
      render json: { error: error_message || 'Training failed', result: result }, status: :internal_server_error
      return
    end

    render json: { job_id: job_id, status: 'started', result: result }, status: :ok
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def warmup
    function_base = params[:function_base] || params.dig(:mask_recommender, :function_base) || 'mask-recommender'
    model_type = params[:model_type].presence || params.dig(:mask_recommender, :model_type).presence
    result = MaskRecommender.warmup(function_base: function_base, model_type: model_type)
    render json: { status: 'ok', result: result }, status: :ok
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def debug
    unless current_user
      render json: { error: 'unauthorized' }, status: :unauthorized
      return
    end

    raw = params.to_unsafe_h
    payload = {
      event: raw['event'],
      level: raw['level'],
      managed_id: raw['managed_id'],
      payload: raw['payload']
    }

    Rails.logger.info("[RecommendMasksDebug] user_id=#{current_user.id} #{payload.to_json}")
    head :accepted
  rescue StandardError => e
    Rails.logger.error("[RecommendMasksDebug] failed: #{e.message}")
    render json: { error: e.message }, status: :unprocessable_entity
  end

  def status
    job_id = params[:id].to_s
    payload = Rails.cache.read(MaskRecommenderJob.cache_key(job_id))

    if payload.blank?
      render json: { status: 'queued' }, status: :ok
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
      :strap_mm,
      :facial_hair_beard_length_mm
    )
  end

  def recommender_columns
    render json: { recommender_columns: FacialMeasurement::RECOMMENDER_COLUMNS }
  end

  def eligible_users
    users = EligibleRecommenderUsersService.call(viewer: current_user)
    render json: { users: users }, status: :ok
  end

  private

  def build_recommendation_response
    function_base = params[:function_base] || params.dig(:mask_recommender, :function_base) || 'mask-recommender'
    model_type = params[:model_type].presence || params.dig(:mask_recommender, :model_type).presence
    resolved_facial_measurements = resolved_facial_measurements_payload
    if resolved_facial_measurements.is_a?(Hash) && resolved_facial_measurements[:error]
      return [resolved_facial_measurements[:status],
              { error: resolved_facial_measurements[:error] }]
    end

    inference = MaskRecommender.infer_with_meta(
      resolved_facial_measurements,
      function_base: function_base,
      model_type: model_type
    )
    masks = merge_user_fit_test_summaries(inference[:masks])
    model = inference[:model]
    data_context = MasksDataContextualizer.call

    [200, { masks: masks, context: data_context, model: model }]
  end

  def merge_user_fit_test_summaries(masks)
    user_id = params[:recommender_user_id].presence
    return masks unless user_id

    summaries = MaskFitTestSummaryService.call(
      viewer: current_user,
      target_user_id: user_id,
      mask_ids: masks.map { |mask| mask['id'] || mask[:id] }
    )

    masks.map do |mask|
      summary = summaries[(mask['id'] || mask[:id]).to_i] || {}
      mask.merge(summary)
    end
  end

  def resolved_facial_measurements_payload
    if params[:recommender_user_id].present?
      LatestRecommenderFacialMeasurementsService.call(
        viewer: current_user,
        recommender_user_id: params[:recommender_user_id]
      )
    else
      facial_measurements.to_h.stringify_keys
    end
  rescue ActionController::ParameterMissing
    { error: 'facial_measurements is required', status: :unprocessable_entity }
  rescue ActiveRecord::RecordNotFound
    { error: 'user not found', status: :not_found }
  rescue LatestRecommenderFacialMeasurementsService::ForbiddenError => e
    { error: e.message, status: :forbidden }
  rescue LatestRecommenderFacialMeasurementsService::MissingMeasurementsError => e
    { error: e.message, status: :unprocessable_entity }
  rescue StandardError => e
    { error: e.message, status: :unprocessable_entity }
  end
end
