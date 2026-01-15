# frozen_string_literal: true

namespace :fit_tests do
  desc 'Migrate notes from results JSONB to notes column'
  task migrate_notes: :environment do
    puts 'Starting migration of fit test notes...'

    total = FitTest.count
    puts "Found #{total} fit tests to process"

    migrated = 0
    skipped = 0

    FitTest.find_each do |fit_test|
      notes = nil

      # Try to get notes from results JSONB
      if fit_test.results.is_a?(Hash)
        # Check qualitative notes first
        if fit_test.results.dig('qualitative', 'notes').present?
          notes = fit_test.results.dig('qualitative', 'notes')
        # Then check quantitative notes
        elsif fit_test.results.dig('quantitative', 'notes').present?
          notes = fit_test.results.dig('quantitative', 'notes')
        end
      end

      if notes.present?
        fit_test.update!(notes: notes)
        migrated += 1
        puts "Migrated notes for FitTest ##{fit_test.id}"
      else
        skipped += 1
      end
    end

    puts "\nMigration complete!"
    puts "Migrated: #{migrated} fit tests"
    puts "Skipped (no notes): #{skipped} fit tests"
  end
end
