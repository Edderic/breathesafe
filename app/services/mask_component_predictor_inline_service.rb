# frozen_string_literal: true

require 'open3'
require 'json'

# Service to predict mask components using pre-trained CRF model
# This service calls a Python script directly, avoiding the need for a separate Flask service
class MaskComponentPredictorInlineService
  PYTHON_SCRIPT_PATH = Rails.root.join('python', 'mask_component_predictor', 'predict_inline.py')

  class << self
    # Predict components for a single mask name
    # @param mask_name [String] The mask name to predict
    # @return [Hash] Prediction result with tokens, breakdown, and components
    def predict(mask_name)
      return fallback_prediction(mask_name) if mask_name.blank?

      stdout, stderr, status = Open3.capture3(
        'python3',
        PYTHON_SCRIPT_PATH.to_s,
        mask_name
      )

      if status.success?
        result = JSON.parse(stdout)
        format_result(result)
      else
        Rails.logger.error("Inline predictor error: #{stderr}")
        fallback_prediction(mask_name)
      end
    rescue JSON::ParserError => e
      Rails.logger.error("Inline predictor JSON parse error: #{e.message}")
      fallback_prediction(mask_name)
    rescue StandardError => e
      Rails.logger.error("Inline predictor error: #{e.message}")
      fallback_prediction(mask_name)
    end

    # Predict components for multiple mask names
    # @param mask_names [Array<String>] Array of mask names to predict
    # @return [Array<Hash>] Array of prediction results
    def predict_batch(mask_names)
      return [] if mask_names.blank?

      # Build command with --batch flag
      cmd = ['python3', PYTHON_SCRIPT_PATH.to_s, '--batch'] + mask_names

      stdout, stderr, status = Open3.capture3(*cmd)

      if status.success?
        result = JSON.parse(stdout)
        result['predictions'].map { |pred| format_result(pred) }
      else
        Rails.logger.error("Inline predictor batch error: #{stderr}")
        mask_names.map { |name| fallback_prediction(name) }
      end
    rescue JSON::ParserError => e
      Rails.logger.error("Inline predictor batch JSON parse error: #{e.message}")
      mask_names.map { |name| fallback_prediction(name) }
    rescue StandardError => e
      Rails.logger.error("Inline predictor batch error: #{e.message}")
      mask_names.map { |name| fallback_prediction(name) }
    end

    # Check if the model is available
    # @return [Hash] Health check result
    def health_check
      if File.exist?(PYTHON_SCRIPT_PATH) && File.exist?(model_path)
        {
          'status' => 'ok',
          'model_loaded' => true,
          'model_path' => model_path.to_s,
          'type' => 'inline'
        }
      else
        {
          'status' => 'error',
          'model_loaded' => false,
          'message' => 'Model file not found',
          'type' => 'inline'
        }
      end
    end

    private

    def model_path
      Rails.root.join('python', 'mask_component_predictor', 'crf_model.pkl')
    end

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
      # Simple rule-based fallback if Python script fails
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
          misc: tokens[2..] || []
        },
        confidence: 0.0,
        fallback: true
      }
    end
  end
end
