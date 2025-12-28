# frozen_string_literal: true

require 'aws-sdk-lambda'
require 'json'

##
# Service for predicting mask components using AWS Lambda CRF model.
#
# This service invokes an AWS Lambda function to predict mask name components
# (brand, model, size, etc.) using a trained CRF model.
#
# Configuration via environment variables:
#   AWS_REGION - AWS region (default: us-east-1)
#   LAMBDA_FUNCTION_NAME - Lambda function name (default: mask-component-predictor)
#   AWS_ACCESS_KEY_ID - AWS credentials (optional if using IAM role)
#   AWS_SECRET_ACCESS_KEY - AWS credentials (optional if using IAM role)
#
# Usage:
#   result = MaskComponentPredictorLambdaService.predict("3M Aura 9205+ N95")
#   results = MaskComponentPredictorLambdaService.predict_batch(["3M 1860s", "Honeywell H910"])
#
class MaskComponentPredictorLambdaService
  REGION = ENV.fetch('AWS_REGION', 'us-east-1')
  FUNCTION_NAME = ENV.fetch('LAMBDA_FUNCTION_NAME', 'mask-component-predictor')

  class << self
    def predict(mask_name)
      payload = { mask_name: mask_name }
      response = invoke_lambda(payload)

      if response['statusCode'] == 200
        result = JSON.parse(response['body'])
        format_result(result)
      else
        Rails.logger.error("Lambda error: #{response['body']}")
        fallback_prediction(mask_name)
      end
    rescue StandardError => e
      Rails.logger.error("Lambda invocation failed: #{e.message}")
      fallback_prediction(mask_name)
    end

    def predict_batch(mask_names)
      payload = { mask_names: mask_names }
      response = invoke_lambda(payload)

      if response['statusCode'] == 200
        result = JSON.parse(response['body'])
        result['predictions'].map { |r| format_result(r) }
      else
        Rails.logger.error("Lambda error: #{response['body']}")
        mask_names.map { |name| fallback_prediction(name) }
      end
    rescue StandardError => e
      Rails.logger.error("Lambda invocation failed: #{e.message}")
      mask_names.map { |name| fallback_prediction(name) }
    end

    def health_check
      # Simple invocation to check if Lambda is accessible
      payload = { mask_name: 'Test' }
      response = invoke_lambda(payload)

      {
        'status' => response['statusCode'] == 200 ? 'ok' : 'error',
        'function_name' => FUNCTION_NAME,
        'region' => REGION,
        'model_loaded' => response['statusCode'] == 200
      }
    rescue StandardError => e
      {
        'status' => 'error',
        'message' => e.message,
        'model_loaded' => false
      }
    end

    private

    def lambda_client
      @lambda_client ||= Aws::Lambda::Client.new(region: REGION)
    end

    def invoke_lambda(payload)
      response = lambda_client.invoke({
        function_name: FUNCTION_NAME,
        invocation_type: 'RequestResponse',
        payload: JSON.generate(payload)
      })

      JSON.parse(response.payload.read)
    end

    def format_result(result)
      {
        mask_name: result['mask_name'],
        tokens: result['tokens'],
        breakdown: result['breakdown'],
        components: result['components'].transform_keys(&:to_sym),
        confidence: result['confidence']
      }
    end

    def fallback_prediction(mask_name)
      # Simple rule-based fallback if Lambda is unavailable
      tokens = MaskTokenizer.tokenize(mask_name)

      {
        mask_name: mask_name,
        tokens: tokens,
        breakdown: tokens.map { |t| { t => 'misc' } },
        components: {
          brand: tokens[0..0] || [],
          model: tokens[1..1] || [],
          size: [],
          color: [],
          style: [],
          strap: [],
          filter_type: [],
          valved: [],
          misc: tokens[2..] || []
        },
        confidence: 0.0,
        fallback: true
      }
    end
  end
end
