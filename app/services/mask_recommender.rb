# frozen_string_literal: true

class MaskRecommender
  class << self
    # New primary entrypoint for inference
    def infer(facial_measurements, mask_ids: nil)
      heroku_env = ENV.fetch('HEROKU_ENVIRONMENT', 'staging')

      payload = {
        method: 'infer',
        facial_measurements: facial_measurements
      }
      payload[:mask_ids] = mask_ids if mask_ids.present?

      response = AwsLambdaInvokeService.call(
        function_name: "mask-recommender-#{heroku_env}",
        payload: payload
      )

      body = Oj.load(response['body'])
      mask_ids = body['mask_id'].map { |_k, v| v }
      proba_fits = body['proba_fit'].map { |_k, v| v }
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
    def train(epochs: 20, data_url: nil, target_col: 'target')
      heroku_env = ENV.fetch('HEROKU_ENVIRONMENT', 'staging')

      payload = { method: 'train' }
      payload[:epochs] = epochs if epochs
      payload[:data_url] = data_url if data_url
      payload[:target_col] = target_col if target_col

      response = AwsLambdaInvokeService.call(
        function_name: "mask-recommender-#{heroku_env}",
        payload: payload
      )

      Oj.load(response['body'])
    end
  end
end
