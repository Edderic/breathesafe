# frozen_string_literal: true

class MaskRecommender
  class << self
    def infer_with_meta(facial_measurements, mask_ids: nil, function_base: 'mask-recommender')
      response = invoke_lambda_infer(
        facial_measurements,
        mask_ids: mask_ids,
        function_base: function_base
      )
      body = parse_lambda_body(response)
      collection = build_mask_collection(body)
      model = body.is_a?(Hash) && body['model'].is_a?(Hash) ? body['model'] : nil
      { masks: collection, model: model }
    end

    # New primary entrypoint for inference
    def infer(facial_measurements, mask_ids: nil, function_base: 'mask-recommender')
      infer_with_meta(
        facial_measurements,
        mask_ids: mask_ids,
        function_base: function_base
      )[:masks]
    end

    # Trigger training on the unified PyTorch Lambda
    # Accepts optional parameters like epochs:, learning_rate:, retrain_with_full:, data_url:, target_col:
    def train(
      epochs: 300,
      learning_rate: 0.00005,
      retrain_with_full: true,
      data_url: nil,
      target_col: 'target',
      function_base: 'mask-recommender'
    )
      heroku_env = lambda_environment

      payload = { method: 'train' }
      payload[:epochs] = epochs if epochs
      payload[:learning_rate] = learning_rate if learning_rate
      payload[:retrain_with_full] = retrain_with_full unless retrain_with_full.nil?
      payload[:data_url] = data_url if data_url
      payload[:target_col] = target_col if target_col
      function_name = "#{function_base}-#{heroku_env}"
      Rails.logger.info("MaskRecommender.train invoking #{function_name}")

      response = AwsLambdaInvokeService.call(
        function_name: function_name,
        payload: payload
      )

      parse_lambda_body(response)
    end

    def warmup(function_base: 'mask-recommender')
      heroku_env = lambda_environment
      function_name = "#{function_base}-#{heroku_env}"
      Rails.logger.info("MaskRecommender.warmup invoking #{function_name}")
      response = AwsLambdaInvokeService.call(
        function_name: function_name,
        payload: { method: 'warmup' }
      )
      parse_lambda_body(response)
    end

    private

    def invoke_lambda_infer(facial_measurements, mask_ids:, function_base:)
      heroku_env = lambda_environment

      payload = {
        method: 'infer',
        facial_measurements: facial_measurements
      }
      payload[:mask_ids] = mask_ids if mask_ids.present?
      function_name = "#{function_base}-#{heroku_env}"
      Rails.logger.info("MaskRecommender.infer invoking #{function_name}")

      AwsLambdaInvokeService.call(
        function_name: function_name,
        payload: payload
      )
    end

    def build_mask_collection(body)
      raise "Lambda error: #{body['error']}" if body.is_a?(Hash) && body['error'].present?

      mask_map = body.is_a?(Hash) ? body['mask_id'] : nil
      proba_map = body.is_a?(Hash) ? body['proba_fit'] : nil
      raise "Invalid lambda response shape: #{body.inspect}" if !mask_map.is_a?(Hash) || !proba_map.is_a?(Hash)

      recommended_pairs = mask_map.each_with_object([]) do |(key, mask_id), rows|
        next unless proba_map.key?(key)

        rows << [mask_id, proba_map[key]]
      end
      recommended_mask_ids = recommended_pairs.map(&:first)
      masks = Mask.with_aggregations.to_a
      masks_by_id = masks.index_by { |m| m['id'] }
      mask_ids_without_recommendation = masks.map { |m| m['id'] } - recommended_mask_ids

      collection = []
      recommended_pairs.each do |mask_id, proba_fit|
        mask = masks_by_id[mask_id]
        next unless mask_perimeter_present?(mask)

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit.to_f
        }.merge(JSON.parse(mask.to_json))
      end

      collection.sort { |a, b| b['proba_fit'] <=> a['proba_fit'] }

      mask_ids_without_recommendation.each.with_index do |mask_id, _index|
        proba_fit = nil
        mask = masks_by_id[mask_id]
        next unless mask_perimeter_present?(mask)

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit
        }.merge(JSON.parse(mask.to_json))
      end

      collection
    end

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

    def mask_perimeter_present?(mask)
      return false if mask.nil?

      raw = mask['perimeter_mm'] || mask['perimeterMm']
      return false if raw.nil?

      value = Float(raw)
      value.positive?
    rescue ArgumentError, TypeError
      false
    end

    def lambda_environment
      explicit = ENV['HEROKU_ENVIRONMENT']
      return explicit if explicit.present?

      return 'production' if Rails.env.production?
      return 'test' if Rails.env.test?

      'development'
    end
  end
end
