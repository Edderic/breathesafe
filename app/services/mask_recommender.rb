# frozen_string_literal: true

class MaskRecommender
  class << self
    # New primary entrypoint for inference
    def infer(facial_measurements, mask_ids: nil, backend: nil)
      heroku_env = ENV.fetch('HEROKU_ENVIRONMENT', 'development')
      backend = (backend || ENV['MASK_RECOMMENDER_BACKEND'] || 'pytorch').to_s.strip.downcase
      function_base = backend == 'rf' ? 'mask-recommender-rf' : 'mask-recommender'

      payload = {
        method: 'infer',
        facial_measurements: facial_measurements
      }
      payload[:mask_ids] = mask_ids if mask_ids.present?

      response = AwsLambdaInvokeService.call(
        function_name: "#{function_base}-#{heroku_env}",
        payload: payload
      )

      body = parse_lambda_body(response)
      raise "Lambda error: #{body['error']}" if body.is_a?(Hash) && body['error'].present?

      mask_map = body.is_a?(Hash) ? body['mask_id'] : nil
      proba_map = body.is_a?(Hash) ? body['proba_fit'] : nil
      raise "Invalid lambda response shape: #{body.inspect}" if !mask_map.is_a?(Hash) || !proba_map.is_a?(Hash)

      mask_ids = mask_map.map { |_k, v| v }
      proba_fits = proba_map.map { |_k, v| v }
      masks = Mask.with_aggregations.to_a
      mask_ids_without_recommendation = masks.map { |m| m['id'] } - mask_ids

      collection = []
      mask_ids.each.with_index do |mask_id, index|
        proba_fit = proba_fits[index]
        mask = masks.find { |m| m['id'] == mask_id }

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit
        }.merge(JSON.parse(mask.to_json))
      end

      collection.sort { |a, b| b['proba_fit'] <=> a['proba_fit'] }

      mask_ids_without_recommendation.each.with_index do |mask_id, _index|
        proba_fit = nil
        mask = masks.find { |m| m['id'] == mask_id }

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit
        }.merge(JSON.parse(mask.to_json))
      end

      collection
    end

    # Trigger training on the unified PyTorch Lambda
    # Accepts optional parameters like epochs:, data_url:, target_col:
    def train(epochs: 20, data_url: nil, target_col: 'target', backend: nil)
      heroku_env = ENV.fetch('HEROKU_ENVIRONMENT', 'staging')
      backend = (backend || ENV['MASK_RECOMMENDER_BACKEND'] || 'pytorch').to_s.strip.downcase
      function_base = backend == 'rf' ? 'mask-recommender-rf' : 'mask-recommender'

      payload = { method: 'train' }
      payload[:epochs] = epochs if epochs
      payload[:data_url] = data_url if data_url
      payload[:target_col] = target_col if target_col

      response = AwsLambdaInvokeService.call(
        function_name: "#{function_base}-#{heroku_env}",
        payload: payload
      )

      parse_lambda_body(response)
    end

    private

    # Handles various Lambda proxy integration response shapes:
    # - {"statusCode":200, "body":"{...}"}
    # - {"statusCode":200, "body":{...}}
    # - Direct body Hash or JSON String
    def parse_lambda_body(response)
      # Already a parsed Hash with a body field
      if response.is_a?(Hash) && response.key?('body')
        body = response['body']
        return body.is_a?(String) ? Oj.load(body) : body
      end

      # If the handler already returned the body Hash directly
      return response if response.is_a?(Hash)

      # If it's a JSON string, parse it
      return Oj.load(response) if response.is_a?(String)

      raise TypeError, "Unexpected Lambda response type: #{response.class}"
    end
  end
end
