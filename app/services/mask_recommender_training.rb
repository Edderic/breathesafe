# frozen_string_literal: true

# Invokes the training entrypoint on the shared mask-recommender Lambda
# for the current environment.
#
# Environment selection is based on HEROKU_ENVIRONMENT:
# - "production", "prod" => mask-recommender-production
# - "staging" or blank => mask-recommender-staging
# - "development", "dev" => mask-recommender-development
#
# Usage:
#   MaskRecommenderTraining.call(payload: { some: "data" })
# Returns the parsed JSON response from the Lambda.
class MaskRecommenderTraining
  WORKFLOW_PARITY_CONFIG = {
    epochs: 1000,
    learning_rate: 0.0001,
    use_diff_perimeter_bins: true
  }.freeze

  class << self
    def call(payload: {}, region: AwsLambdaInvokeService::DEFAULT_REGION)
      function_name = build_function_name(resolve_environment)
      payload = WORKFLOW_PARITY_CONFIG.merge(payload)
      payload = payload.merge(method: 'train') unless payload.key?(:method)
      AwsLambdaInvokeService.call(function_name: function_name, payload: payload, region: region)
    end

    private

    def resolve_environment
      raw_env = ENV.fetch('HEROKU_ENVIRONMENT', '').to_s.strip.downcase

      return 'production' if %w[production prod].include?(raw_env)
      return 'development' if %w[development dev].include?(raw_env)
      return 'staging' if raw_env.empty? || %w[staging].include?(raw_env)

      raise(ArgumentError,
            "Unsupported HEROKU_ENVIRONMENT: '#{raw_env}'. Use 'development', 'staging', or 'production'.")
    end

    def build_function_name(env)
      "mask-recommender-#{env}"
    end
  end
end
