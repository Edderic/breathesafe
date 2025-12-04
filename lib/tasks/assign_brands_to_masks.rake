# frozen_string_literal: true

namespace :masks do
  desc 'Interactively assign brands to masks based on string matching and edit distance'
  task assign_brands: :environment do
    require 'io/console'

    # Levenshtein distance implementation
    def levenshtein_distance(str1, str2)
      n = str1.length
      m = str2.length
      return m if n.zero?
      return n if m.zero?

      prev = (0..m).to_a
      cur = Array.new(m + 1, 0)
      (1..n).each do |i|
        cur[0] = i
        (1..m).each do |j|
          cost = str1[i - 1] == str2[j - 1] ? 0 : 1
          cur[j] = [
            cur[j - 1] + 1,
            prev[j] + 1,
            prev[j - 1] + cost
          ].min
        end
        prev, cur = cur, prev
      end
      prev[m]
    end

    # Normalize string: downcase and trim whitespace
    def normalize_string(str)
      str.to_s.downcase.strip
    end

    # Calculate similarity score between mask code and brand name
    def calculate_similarity(mask_code, brand_name)
      norm_mask = normalize_string(mask_code)
      norm_brand = normalize_string(brand_name)

      # String matching score: 1 if brand name is contained in mask code, 0 otherwise
      string_match_score = norm_mask.include?(norm_brand) ? 1.0 : 0.0

      # Edit distance score: 1 - (edit_distance / max_length)
      max_length = [norm_mask.length, norm_brand.length].max
      edit_dist = levenshtein_distance(norm_mask, norm_brand)
      edit_distance_score = max_length.zero? ? 0.0 : 1.0 - (edit_dist.to_f / max_length)

      # Average the two scores
      (string_match_score + edit_distance_score) / 2.0
    end

    # Find masks without brand_id
    masks = Mask.where(brand_id: nil).order(:id)
    total_masks = masks.count

    if total_masks.zero?
      puts "No masks found without brand_id. All masks already have brands assigned."
      exit 0
    end

    puts "Found #{total_masks} masks without brand_id."
    puts "Starting interactive brand assignment...\n\n"

    # Get all brands
    brands = Brand.all.order(:name)
    if brands.empty?
      puts "No brands found in database. Please run 'rake brands:prepopulate' first."
      exit 1
    end

    assigned_count = 0
    skipped_count = 0
    auto_skipped_mask_ids = []

    threshold = 0.01

    masks.each_with_index do |mask, index|
      current_number = index + 1
      puts "=" * 80
      puts "Processing mask #{current_number} of #{total_masks}"
      puts "=" * 80
      puts "Mask ID: #{mask.id}"
      puts "Unique Internal Model Code: #{mask.unique_internal_model_code}"
      puts "Current Brand ID: #{mask.brand_id || 'None'}"
      puts

      # Calculate similarity scores for all brands
      scores = brands.map do |brand|
        score = calculate_similarity(mask.unique_internal_model_code, brand.name)
        { brand: brand, score: score }
      end

      # Sort by score descending and take top 10
      top_matches = scores.sort_by { |s| -s[:score] }.first(10)

      # Filter by threshold (0.1)
      matches_above_threshold = top_matches.select { |m| m[:score] >= threshold }

      if matches_above_threshold.empty?
        puts "No matches found above threshold (#{threshold}). Auto-skipping this mask."
        auto_skipped_mask_ids << mask.id
        skipped_count += 1
        puts
        next
      end

      # Display top matches
      puts "Top matches (score >= #{threshold}):"
      puts "-" * 80
      puts "0. Skip this mask"
      matches_above_threshold.each_with_index do |match, idx|
        number = idx + 1
        brand = match[:brand]
        score = match[:score]
        puts "#{number}. Brand: #{brand.name} (ID: #{brand.id}) - Score: #{score.round(4)}"
      end
      puts "-" * 80
      puts

      # Get user input
      begin
        print "Enter your choice (0-#{matches_above_threshold.length}): "
        input = STDIN.gets.chomp.strip

        choice = input.to_i

        if choice.zero?
          puts "Skipping mask #{mask.id}"
          skipped_count += 1
        elsif choice >= 1 && choice <= matches_above_threshold.length
          selected_match = matches_above_threshold[choice - 1]
          selected_brand = selected_match[:brand]

          # Update the mask immediately
          mask.brand_id = selected_brand.id
          if mask.save
            # Reload to ensure we have the latest data
            mask.reload
            puts "✓ Assigned brand '#{selected_brand.name}' (ID: #{selected_brand.id}) to mask #{mask.id}"
            puts "  Mask brand_id is now: #{mask.brand_id}"
            assigned_count += 1
          else
            puts "✗ Error saving mask: #{mask.errors.full_messages.join(', ')}"
            skipped_count += 1
          end
        else
          puts "Invalid choice. Please enter a number between 0 and #{matches_above_threshold.length}."
          redo
        end
      rescue Interrupt
        puts "\n\nInterrupted by user. Exiting..."
        break
      rescue StandardError => e
        puts "Error processing input: #{e.message}"
        puts "Skipping this mask."
        skipped_count += 1
      end

      puts
    end

    # Summary
    puts "\n" + "=" * 80
    puts "SUMMARY"
    puts "=" * 80
    puts "Total masks processed: #{total_masks}"
    puts "Brands assigned: #{assigned_count}"
    puts "Masks skipped: #{skipped_count}"
    puts

    if auto_skipped_mask_ids.any?
      puts "Auto-skipped mask IDs (no matches above threshold):"
      puts auto_skipped_mask_ids.join(', ')
      puts
    end

    puts "Task completed!"
  end
end
