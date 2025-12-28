# frozen_string_literal: true

namespace :mask_predictor do
  desc 'Export training data for mask component predictor'
  task export_training_data: :environment do
    puts 'Exporting mask breakdown training data...'
    puts '-' * 80

    # Get latest breakdown for each mask
    training_data = []

    Mask.find_each do |mask|
      latest_event = MaskEvent.where(mask_id: mask.id, event_type: 'breakdown_updated')
                              .order(created_at: :desc)
                              .first

      next unless latest_event

      breakdown = latest_event.data['breakdown']
      next unless breakdown&.any?

      training_data << {
        mask_id: mask.id,
        mask_name: mask.unique_internal_model_code,
        breakdown: breakdown
      }
    end

    puts "Collected #{training_data.length} annotated masks"

    # Write to JSON file
    output_path = Rails.root.join('python', 'mask_component_predictor', 'training_data.json')
    File.write(output_path, JSON.pretty_generate(training_data))

    puts "✓ Training data exported to #{output_path}"
    puts '-' * 80

    # Show statistics
    all_categories = training_data.flat_map { |d| d[:breakdown].map { |item| item.values.first } }
    category_counts = all_categories.group_by(&:itself).transform_values(&:count)

    puts "\nCategory distribution:"
    category_counts.sort_by { |_k, v| -v }.each do |category, count|
      puts "  #{category}: #{count}"
    end
  end

  desc 'Train CRF model for mask component prediction'
  task train: :environment do
    # First export training data
    Rake::Task['mask_predictor:export_training_data'].invoke

    puts "\nTraining CRF model..."
    puts '-' * 80

    # Run Python training script
    python_dir = Rails.root.join('python', 'mask_component_predictor')
    result = system("cd #{python_dir} && python3 train_model.py")

    if result
      puts "\n✓ Model training completed successfully"
    else
      puts "\n✗ Model training failed"
      exit 1
    end
  end

  desc 'Test mask component predictor (optional: PORT=5000)'
  task test: :environment do
    require 'net/http'
    require 'json'

    # Get port from environment variable or default to 5000
    port = ENV['PORT'] || '5000'
    base_url = "http://localhost:#{port}"

    # Check if Python service is running
    begin
      uri = URI("#{base_url}/health")
      response = Net::HTTP.get_response(uri)

      if response.code != '200'
        puts "Error: Python service returned status #{response.code}"
        puts "Start with: cd python/mask_component_predictor && python3 app.py #{port}"
        exit 1
      end

      health = JSON.parse(response.body)

      unless health['model_loaded']
        puts "Error: Model not loaded in Python service"
        puts "Run: rails mask_predictor:train"
        exit 1
      end
    rescue Errno::ECONNREFUSED
      puts "Error: Python service not running on port #{port}"
      puts "Start with: cd python/mask_component_predictor && python3 app.py #{port}"
      exit 1
    rescue JSON::ParserError => e
      puts "Error: Invalid response from Python service"
      puts "Response body: #{response&.body&.inspect}"
      puts "Make sure the service is running: cd python/mask_component_predictor && python3 app.py #{port}"
      exit 1
    rescue StandardError => e
      puts "Error connecting to Python service: #{e.class} - #{e.message}"
      puts "Start with: cd python/mask_component_predictor && python3 app.py #{port}"
      exit 1
    end

    # Test with some examples
    test_masks = [
      '3M 1860s',
      'Zimi ZM9233 w/ Headstraps',
      'Honeywell H910 Plus',
      'BreatheTeq - Large'
    ]

    puts "Testing mask component predictor on port #{port}..."
    puts '-' * 80

    test_masks.each do |mask_name|
      uri = URI("#{base_url}/predict")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = { mask_name: mask_name }.to_json

      response = http.request(request)
      result = JSON.parse(response.body)

      puts "\nMask: #{mask_name}"
      puts "Breakdown:"
      result['breakdown'].each do |item|
        token = item.keys.first
        category = item.values.first
        puts "  #{token} -> #{category}"
      end
      puts "Confidence: #{(result['confidence'] * 100).round(1)}%" if result['confidence']
    end

    puts "\n" + '-' * 80
    puts "✓ Tests completed"
  end
end
