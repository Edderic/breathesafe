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
      client_options = {
        region: region,
        access_key_id: ENV['AWS_ACCESS_KEY_ID'],
        secret_access_key: ENV['AWS_SECRET_ACCESS_KEY'],
        http_open_timeout: 15,
        http_read_timeout: 920,
        retry_limit: 3
      }

      # If SSL verification is explicitly disabled via environment variable
      if ENV['AWS_SSL_VERIFY'] == 'false'
        require 'openssl'
        # NOTE: This is less secure and should only be used in development/staging
        # The AWS SDK will use the default HTTP client with SSL verification disabled
        client_options[:ssl_verify_peer] = false
      end

      Aws::Lambda::Client.new(client_options)
    end

    def invoke_lambda(aws_lambda, function_name, payload)
      result = aws_lambda.invoke(function_name: function_name, payload: payload.to_json)
      parse_lambda_response(result)
    rescue Seahorse::Client::NetworkingError => e
      # Handle SSL certificate verification errors
      raise unless e.message.include?('certificate verify failed') || e.message.include?('CRL')

      Rails.logger.error("AWS Lambda SSL error: #{e.message}")
      Rails.logger.error('If this persists, you may need to set AWS_SSL_VERIFY=false (development/staging only)')
      raise "AWS Lambda connection failed due to SSL certificate verification: #{e.message}. " \
            'This may be due to outdated certificate stores or unreachable CRL servers.'
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
    # Assumes ./scripts/run_local_recommender.sh serves HTTP on localhost:5055
    def invoke_local(function_name:, payload: {})
      Rails.logger.debug("Running lambda #{function_name}...")
      uri = URI.parse(ENV.fetch('LOCAL_LAMBDA_URL', 'http://127.0.0.1:5055/mask_recommender'))
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
