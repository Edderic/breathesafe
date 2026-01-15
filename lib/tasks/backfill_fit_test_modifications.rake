# frozen_string_literal: true

namespace :fit_tests do
  desc 'Backfill mask_modded column for existing fit tests'
  task backfill_mask_modded: :environment do
    puts 'Starting backfill of fit_tests.mask_modded column...'

    total = FitTest.where(mask_modded: nil).count
    puts "Found #{total} fit tests to backfill"

    updated = 0
    FitTest.where(mask_modded: nil).find_each do |fit_test|
      fit_test.update!(mask_modded: false)
      updated += 1
    end
    puts "Updated #{updated} fit tests to have mask_modded = false"

    puts 'Backfill complete!'
  end
end
