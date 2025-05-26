class MaskRecommender
  class << self
    def call(facial_measurements)
      response = AwsLambdaInvokeService.call(
        function_name: 'mask-recommender',
        payload: facial_measurements
      )
    end
  end
end
