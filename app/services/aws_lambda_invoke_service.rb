# frozen_string_literal: true

# This service invokes an AWS Lambda function and logs the request, response, and errors.
#

class AwsLambdaInvokeService
  DEFAULT_REGION = 'us-east-1'
  MAX_BODY_ROWS = 100
  class << self
    def call(function_name:, payload: {}, region: DEFAULT_REGION)
      aws_lambda = init_aws_lambda_client(region)

      invoke_lambda(aws_lambda, function_name, payload)
    end

    private

    def init_aws_lambda_client(region)
      Aws::Lambda::Client.new({
                                region: region,
                                access_key_id: ENV['AWS_ACCESS_KEY_ID'],
                                secret_access_key: ENV['AWS_SECRET_ACCESS_KEY']
                              })
    end

    def invoke_lambda(aws_lambda, function_name, payload)
      result = aws_lambda.invoke(function_name: function_name, payload: payload.to_json)
      parse_lambda_response(result)
    end

    def parse_lambda_response(result)
      raw_response = +''
      result.payload.each { |chunk| raw_response << chunk }
      Oj.load(raw_response)
    rescue StandardError => e
      raise "Failed to parse Lambda response: #{e.message}"
    end
  end
end
