# frozen_string_literal: true

class MaskRecommenderJob < ApplicationJob
  queue_as :default

  CACHE_TTL = 2.hours

  def self.cache_key(job_id)
    "mask_recommender:jobs:#{job_id}"
  end

  def perform(job_id:, facial_measurements:, function_base:, recommender_user_id: nil, viewer_id: nil)
    cache_key = self.class.cache_key(job_id)
    Rails.cache.write(
      cache_key,
      { status: 'running', started_at: Time.current.iso8601 },
      expires_in: CACHE_TTL
    )

    inference = MaskRecommender.infer_with_meta(
      facial_measurements,
      function_base: function_base
    )
    masks = inference[:masks]
    if recommender_user_id.present? && viewer_id.present?
      viewer = User.find_by(id: viewer_id)
      if viewer
        summaries = MaskFitTestSummaryService.call(
          viewer: viewer,
          target_user_id: recommender_user_id,
          mask_ids: masks.map { |mask| mask['id'] || mask[:id] }
        )
        masks = masks.map do |mask|
          summary = summaries[(mask['id'] || mask[:id]).to_i] || {}
          mask.merge(summary)
        end
      end
    end
    model = inference[:model]

    Rails.cache.write(
      cache_key,
      {
        status: 'complete',
        completed_at: Time.current.iso8601,
        result: masks,
        model: model
      },
      expires_in: CACHE_TTL
    )
  rescue StandardError => e
    Rails.cache.write(
      cache_key,
      {
        status: 'failed',
        failed_at: Time.current.iso8601,
        error: e.message
      },
      expires_in: CACHE_TTL
    )
    raise
  end
end
