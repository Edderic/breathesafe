# frozen_string_literal: true

# This service invokes an AWS Lambda function and logs the request, response, and errors.
#
require 'net/http'
require 'uri'

class AwsLambdaInvokeService
  DEFAULT_REGION = 'us-east-1'
  MAX_BODY_ROWS = 100
  class << self
    def call(function_name:, payload: {}, region: DEFAULT_REGION)
      if local_mode?
        invoke_local(function_name: function_name, payload: payload)
      else
        aws_lambda = init_aws_lambda_client(region)
        invoke_lambda(aws_lambda, function_name, payload)
      end
    end

    private

    def init_aws_lambda_client(region)
      # Increase read timeout to support long-running Lambda (up to 15 minutes)
      Aws::Lambda::Client.new({
                                region: region,
                                access_key_id: ENV['AWS_ACCESS_KEY_ID'],
                                secret_access_key: ENV['AWS_SECRET_ACCESS_KEY'],
                                http_open_timeout: 15,
                                http_read_timeout: 920,
                                retry_limit: 3
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

    def local_mode?
      env = ENV.fetch('HEROKU_ENVIRONMENT', Rails.env.to_s).to_s.downcase
      %w[development dev].include?(env)
    end

    # Call the locally served lambda (same payload shape & response body)
    # Assumes ./scripts/run_lambda_locally.sh serves HTTP on localhost:3000
    def invoke_local(function_name:, payload: {})
      Rails.logger.debug("Running lambda #{function_name}...")
      uri = URI.parse(ENV.fetch('LOCAL_LAMBDA_URL', 'http://localhost:9000/2015-03-31/functions/function/invocations'))
      http = Net::HTTP.new(uri.host, uri.port)
      http.read_timeout = 900
      req = Net::HTTP::Post.new(uri.request_uri)
      req['Content-Type'] = 'application/json'
      req.body = payload.to_json
      res = http.request(req)
      raise "Local lambda HTTP #{res.code}: #{res.body}" unless res.is_a?(Net::HTTPSuccess)

      # The local server should already return the final body JSON
      Oj.load(res.body)
    rescue StandardError => e
      raise "Failed to call local lambda: #{e.message}"
    end
  end
end
