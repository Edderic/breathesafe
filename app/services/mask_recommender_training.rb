# frozen_string_literal: true

# Invokes the training AWS Lambda function for the current environment.
#
# Environment selection is based on HEROKU_ENVIRONMENT:
# - "production", "prod" => mask-recommender-training-production
# - "staging", "development", "dev", or blank => mask-recommender-training-staging
#
# Usage:
#   MaskRecommenderTraining.call(payload: { some: "data" })
# Returns the parsed JSON response from the Lambda.
class MaskRecommenderTraining
  class << self
    def call(payload: {}, region: AwsLambdaInvokeService::DEFAULT_REGION)
      function_name = build_function_name(resolve_environment)
      AwsLambdaInvokeService.call(function_name: function_name, payload: payload, region: region)
    end

    private

    def resolve_environment
      raw_env = ENV.fetch('HEROKU_ENVIRONMENT', '').to_s.strip.downcase

      return 'production' if %w[production prod].include?(raw_env)
      return 'staging' if raw_env.empty? || %w[staging development dev].include?(raw_env)

      raise(ArgumentError, "Unsupported HEROKU_ENVIRONMENT: '#{raw_env}'. Use 'staging' or 'production'.")
    end

    def build_function_name(env)
      "mask-recommender-training-#{env}"
    end
  end
end
