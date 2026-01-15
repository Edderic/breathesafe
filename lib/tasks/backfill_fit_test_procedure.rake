# frozen_string_literal: true

namespace :fit_tests do
  desc 'Backfill procedure column for existing fit tests'
  task backfill_procedure: :environment do
    puts 'Starting backfill of fit_tests.procedure column...'

    total = FitTest.where(procedure: nil).count
    puts "Found #{total} fit tests to backfill"

    updated = 0
    skipped = 0

    FitTest.where(procedure: nil).find_each do |fit_test|
      procedure = detect_procedure(fit_test)

      if procedure
        fit_test.update!(procedure: procedure)
        updated += 1
      else
        skipped += 1
      end

      # Progress indicator every 100 records
      if ((updated + skipped) % 100).zero?
        puts "Processed #{updated + skipped}/#{total} (#{updated} updated, #{skipped} skipped)"
      end
    end

    puts "\nBackfill complete!"
    puts "Updated: #{updated} fit tests"
    puts "Skipped (could not determine): #{skipped} fit tests"
  end

  def detect_procedure(fit_test)
    results = fit_test.results || {}
    qualitative = results['qualitative'] || {}
    quantitative = results['quantitative'] || {}

    qualitative_procedure = qualitative['procedure']
    quantitative_procedure = quantitative['procedure']

    # Check qualitative procedure
    if qualitative_procedure && qualitative_procedure != 'Skipping' && (qualitative_procedure == 'Full OSHA')
      return 'qualitative_full_osha'
    end

    # Check quantitative procedure
    if quantitative_procedure && quantitative_procedure != 'Skipping'
      return 'quantitative_osha_fast' if quantitative_procedure == 'OSHA Fast Filtering Face Piece Respirators'
      return 'quantitative_full_osha' if quantitative_procedure == 'Full OSHA'
      return 'quantitative_w1' if quantitative_procedure == 'W1'
    end

    # Try to infer from exercise data
    quantitative_exercises = quantitative['exercises']
    if quantitative_exercises.is_a?(Array) && quantitative_exercises.length.positive?
      has_quant_data = quantitative_exercises.any? { |ex| ex && ex['fit_factor'] && ex['fit_factor'].to_s.strip != '' }

      if has_quant_data
        exercise_count = quantitative_exercises.length
        exercise_names = quantitative_exercises.map { |ex| (ex['name'] || '').downcase }

        # Check for W1 specific exercises (4 exercises with specific names)
        if exercise_count == 4 && (exercise_names.include?('jaw movement') || exercise_names.include?('head movement'))
          return 'quantitative_w1'
        end

        # Full OSHA typically has 9 exercises, OSHA Fast has 5
        if exercise_count >= 8
          return 'quantitative_full_osha'
        elsif exercise_count >= 4
          return 'quantitative_osha_fast'
        end
      end
    end

    # Check qualitative exercises
    qualitative_exercises = qualitative['exercises']
    if qualitative_exercises.is_a?(Array) && qualitative_exercises.length.positive?
      has_qual_data = qualitative_exercises.any? { |ex| ex && ex['result'] && ex['result'].to_s.strip != '' }
      return 'qualitative_full_osha' if has_qual_data
    end

    # Could not determine
    nil
  end
end
