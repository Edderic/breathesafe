# frozen_string_literal: true

require 'json'
begin
  require 'aws-sdk-s3'
rescue LoadError
  # Allow local development without aws-sdk-s3; S3 reads will raise if actually needed.
end

class LatestMaskRecommenderMetricsService
  class << self
    def call
      new.call
    end
  end

  def call
    metrics = load_metrics
    return unavailable_payload if metrics.blank?

    {
      available: true,
      timestamp: metrics['timestamp'],
      model_type: metrics['model_type'],
      random_seed: metrics['random_seed'],
      validation_roc_auc: metrics['roc_auc'],
      cross_validation_folds: metrics.dig('cross_validation', 'num_folds'),
      cross_validation_top_1_hit_rate_mean: metrics.dig('cross_validation', 'top_1_hit_rate_mean'),
      cross_validation_top_3_hit_rate_mean: metrics.dig('cross_validation', 'top_3_hit_rate_mean'),
      cross_validation_top_5_hit_rate_mean: metrics.dig('cross_validation', 'top_5_hit_rate_mean'),
      cross_validation_user_level_mean_roc_auc: metrics.dig('cross_validation', 'user_level_mean_roc_auc'),
      saved_model_training_scope: metrics['saved_model_training_scope'],
      top_k_chart_artifact: metrics['cross_validation_top_k_hit_rate_artifact']
    }
  rescue StandardError => e
    Rails.logger.warn("LatestMaskRecommenderMetricsService unavailable: #{e.class}: #{e.message}")
    unavailable_payload(error: e.message)
  end

  private

  def unavailable_payload(error: nil)
    {
      available: false,
      error: error,
      timestamp: nil,
      model_type: nil,
      random_seed: nil,
      validation_roc_auc: nil,
      cross_validation_folds: nil,
      cross_validation_top_1_hit_rate_mean: nil,
      cross_validation_top_3_hit_rate_mean: nil,
      cross_validation_top_5_hit_rate_mean: nil,
      cross_validation_user_level_mean_roc_auc: nil,
      saved_model_training_scope: nil,
      top_k_chart_artifact: nil
    }
  end

  def load_metrics
    if local_env?
      load_local_metrics
    else
      load_s3_metrics
    end
  end

  def load_local_metrics
    metrics_paths = Dir.glob(File.join(local_model_root, '*/custom_metrics.json')).sort
    return nil if metrics_paths.empty?

    JSON.parse(File.read(metrics_paths.last))
  end

  def load_s3_metrics
    raise 'aws-sdk-s3 not available' unless defined?(Aws::S3::Client)

    pointer_payload = JSON.parse(read_s3_object(s3_bucket, latest_pointer_key))
    metrics_key = pointer_payload['metrics_key']
    return nil if metrics_key.blank?

    JSON.parse(read_s3_object(s3_bucket, metrics_key))
  end

  def read_s3_object(bucket, key)
    s3_client.get_object(bucket: bucket, key: key).body.read
  end

  def s3_client
    @s3_client ||= Aws::S3::Client.new(region: s3_region)
  end

  def s3_region
    ENV['AWS_REGION'].presence || ENV['S3_BUCKET_REGION'].presence || 'us-east-1'
  end

  def local_env?
    Rails.env.development? || Rails.env.test?
  end

  def local_model_root
    ENV['MASK_RECOMMENDER_LOCAL_MODEL_DIR'].presence || Rails.root.join('python/mask_recommender/local_models').to_s
  end

  def latest_pointer_key
    'mask_recommender/models/custom_latest.json'
  end

  def s3_bucket
    case environment_name
    when 'production'
      'breathesafe'
    when 'staging'
      'breathesafe-staging'
    else
      'breathesafe-development'
    end
  end

  def environment_name
    ENV['HEROKU_ENVIRONMENT'].presence || Rails.env
  end
end
