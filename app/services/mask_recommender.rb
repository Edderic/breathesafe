class MaskRecommender
  class << self
    def call(facial_measurements)
      response = AwsLambdaInvokeService.call(
        function_name: 'mask-recommender-inference', # New inference function
        payload: { facial_measurements: facial_measurements }
      )

      body = Oj.load(response['body'])
      mask_ids = body['mask_id'].map{|k,v| v}
      proba_fits = body['proba_fit'].map{|k,v| v}
      masks = Mask.with_aggregations.to_a
      mask_ids_without_recommendation = masks.map{|m| m['id']} - mask_ids

      collection = []
      mask_ids.each.with_index do |mask_id, index|
        proba_fit = proba_fits[index]
        mask = masks.find{|m| m['id'] == mask_id}

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit
        }.merge(JSON.parse(mask.to_json))
      end

      collection.sort{|a,b| b['proba_fit'] <=> a['proba_fit']}

      mask_ids_without_recommendation.each.with_index do |mask_id, index|
        proba_fit = nil
        mask = masks.find{|m| m['id'] == mask_id}

        collection << {
          'id' => mask_id,
          'proba_fit' => proba_fit
        }.merge(JSON.parse(mask.to_json))
      end

      collection
    end
  end
end
