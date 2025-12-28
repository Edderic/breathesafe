# frozen_string_literal: true

require 'net/http'
require 'json'

class MaskComponentPredictorService
  PYTHON_SERVICE_URL = ENV.fetch('MASK_PREDICTOR_URL', 'http://localhost:5000')

  class << self
    def predict(mask_name)
      uri = URI("#{PYTHON_SERVICE_URL}/predict")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = { mask_name: mask_name }.to_json

      response = http.request(request)

      if response.code == '200'
        result = JSON.parse(response.body)
        format_result(result)
      else
        Rails.logger.error("Mask predictor error: #{response.body}")
        fallback_prediction(mask_name)
      end
    rescue StandardError => e
      Rails.logger.error("Mask predictor connection error: #{e.message}")
      fallback_prediction(mask_name)
    end

    def predict_batch(mask_names)
      uri = URI("#{PYTHON_SERVICE_URL}/predict_batch")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = { mask_names: mask_names }.to_json

      response = http.request(request)

      if response.code == '200'
        result = JSON.parse(response.body)
        result['predictions'].map { |pred| format_result(pred) }
      else
        Rails.logger.error("Mask predictor batch error: #{response.body}")
        mask_names.map { |name| fallback_prediction(name) }
      end
    rescue StandardError => e
      Rails.logger.error("Mask predictor batch connection error: #{e.message}")
      mask_names.map { |name| fallback_prediction(name) }
    end

    def health_check
      uri = URI("#{PYTHON_SERVICE_URL}/health")
      response = Net::HTTP.get_response(uri)

      if response.code == '200'
        JSON.parse(response.body)
      else
        { 'status' => 'error', 'model_loaded' => false }
      end
    rescue StandardError => e
      { 'status' => 'error', 'message' => e.message, 'model_loaded' => false }
    end

    private

    def format_result(result)
      {
        mask_name: result['mask_name'],
        tokens: result['tokens'],
        breakdown: result['breakdown'],
        components: {
          brand: result['components']['brand'],
          model: result['components']['model'],
          size: result['components']['size'],
          color: result['components']['color'],
          style: result['components']['style'],
          strap: result['components']['strap'],
          filter_type: result['components']['filter_type'],
          valved: result['components']['valved'],
          misc: result['components']['misc']
        },
        confidence: result['confidence']
      }
    end

    def fallback_prediction(mask_name)
      # Simple rule-based fallback if Python service is unavailable
      tokens = MaskTokenizer.tokenize(mask_name)

      {
        mask_name: mask_name,
        tokens: tokens,
        breakdown: tokens.map { |t| { t => 'misc' } },
        components: {
          brand: tokens.first ? [tokens.first] : [],
          model: tokens.length > 1 ? [tokens[1]] : [],
          size: [],
          color: [],
          style: [],
          strap: [],
          filter_type: [],
          valved: [],
          misc: tokens[2..-1] || []
        },
        confidence: 0.0,
        fallback: true
      }
    end
  end
end
