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

    # Levenshtein distance for words (arrays)
    def levenshtein_distance_words(words1, words2)
      n = words1.length
      m = words2.length
      return m if n.zero?
      return n if m.zero?

      prev = (0..m).to_a
      cur = Array.new(m + 1, 0)
      (1..n).each do |i|
        cur[0] = i
        (1..m).each do |j|
          cost = words1[i - 1] == words2[j - 1] ? 0 : 1
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

    # Calculate similarity score between mask code and brand name
    def calculate_similarity(mask_code, brand_name)
      norm_mask = normalize_string(mask_code)
      norm_brand = normalize_string(brand_name)

      # Score 1: Character-based Levenshtein distance similarity
      max_char_length = [norm_mask.length, norm_brand.length].max
      if max_char_length.zero?
        char_distance_score = 0.0
      else
        char_edit_dist = levenshtein_distance(norm_mask, norm_brand)
        char_distance_score = 1.0 - (char_edit_dist.to_f / max_char_length)
      end

      # Score 2: Word-based Levenshtein distance similarity
      # Split into words (split on whitespace and filter empty strings)
      mask_words = norm_mask.split(/\s+/).reject(&:empty?)
      brand_words = norm_brand.split(/\s+/).reject(&:empty?)

      max_words = [mask_words.length, brand_words.length].max
      if max_words.zero?
        word_distance_score = 0.0
      else
        word_edit_dist = levenshtein_distance_words(brand_words, mask_words)
        word_distance_score = 1.0 / (0.01 + word_edit_dist.to_f)
      end

      # Score 3: Word containment - check if any brand word is contained in any mask word
      word_containment_score = 0.0
      if brand_words.any? && mask_words.any?
        word_containment_score = brand_words.any? { |brand_word|
          mask_words.any? { |mask_word| mask_word.include?(brand_word) }
        } ? 1.0 : 0.0
      end

      # Average the three scores
      (char_distance_score + word_distance_score + word_containment_score) / 3.0
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

    threshold = 0.001

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
        score = calculate_similarity(mask.unique_internal_model_code.downcase, brand.name.downcase)
        { brand: brand, score: score }
      end

      # Sort by score descending and take top 10
      top_matches = scores.sort_by { |s| -s[:score] }.first(200)

      # Filter by threshold (0.1)
      matches_above_threshold = top_matches.select { |m| m[:score] >= threshold }

      if matches_above_threshold.empty?
        puts "No matches found above threshold (#{threshold}). Auto-skipping this mask."
        auto_skipped_mask_ids << mask.id
        skipped_count += 1
        puts
        next
      end

      # Display matches with pagination (10 at a time)
      start_index = 0
      page_size = 10
      total_matches = matches_above_threshold.length

      loop do
        # Calculate which matches to show on this page
        end_index = [start_index + page_size, total_matches].min
        current_page_matches = matches_above_threshold[start_index...end_index]

        puts "Top matches (score >= #{threshold}):"
        puts "-" * 80
        puts "0. Skip this mask"
        current_page_matches.each_with_index do |match, idx|
          number = start_index + idx + 1
          brand = match[:brand]
          score = match[:score]
          puts "#{number}. Brand: #{brand.name} (ID: #{brand.id}) - Score: #{score.round(4)}"
        end
        if end_index < total_matches
          puts "m. Show more options (#{end_index} of #{total_matches} shown)"
        end
        puts "-" * 80
        puts

        # Get user input
        begin
          max_choice = end_index
          print "Enter your choice (0-#{max_choice}"
          print ", m for more" if end_index < total_matches
          print "): "
          input = STDIN.gets.chomp.strip.downcase

          if input == 'm'
            if end_index < total_matches
              start_index = end_index
              puts
              next
            else
              puts "No more options to show."
              redo
            end
          end

          choice = input.to_i

          if choice.zero?
            puts "Skipping mask #{mask.id}"
            skipped_count += 1
            break
          elsif choice >= 1 && choice <= total_matches
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
            break
          else
            puts "Invalid choice. Please enter a number between 0 and #{total_matches}"
            puts "or 'm' to show more options." if end_index < total_matches
            redo
          end
        rescue Interrupt
          puts "\n\nInterrupted by user. Exiting..."
          exit
        rescue StandardError => e
          puts "Error processing input: #{e.message}"
          puts "Skipping this mask."
          skipped_count += 1
          break
        end
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
