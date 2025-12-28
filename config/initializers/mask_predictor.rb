# frozen_string_literal: true

# Mask Component Predictor Configuration
#
# This initializer sets up the mask component predictor service.
# It can use either a local Flask service or AWS Lambda.
#
# Configuration:
#   USE_LAMBDA_PREDICTOR=true  - Use AWS Lambda (recommended for production)
#   USE_LAMBDA_PREDICTOR=false - Use local Flask service (development)
#
# Lambda configuration (when USE_LAMBDA_PREDICTOR=true):
#   AWS_REGION=us-east-1
#   LAMBDA_FUNCTION_NAME=mask-component-predictor
#   AWS_ACCESS_KEY_ID=...
#   AWS_SECRET_ACCESS_KEY=...
#
# Flask configuration (when USE_LAMBDA_PREDICTOR=false):
#   MASK_PREDICTOR_URL=http://localhost:1234
#   MASK_PREDICTOR_PORT=1234
#

Rails.application.config.use_lambda_predictor = ENV.fetch('USE_LAMBDA_PREDICTOR', 'false') == 'true'

if Rails.application.config.use_lambda_predictor
  Rails.logger.info "✓ Mask predictor: AWS Lambda (#{ENV.fetch('LAMBDA_FUNCTION_NAME', 'mask-component-predictor')})"
elsif ENV['USE_FLASK_PREDICTOR'] == 'true'
  port = ENV.fetch('MASK_PREDICTOR_PORT', '5000')
  Rails.logger.info "✓ Mask predictor: Flask service (port #{port})"
else
  Rails.logger.info "✓ Mask predictor: Inline Python (pre-trained model)"
end
