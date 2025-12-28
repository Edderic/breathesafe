# frozen_string_literal: true

namespace :fit_tests do
  desc 'Backfill mask_modded column for existing fit tests'
  task backfill_mask_modded: :environment do
    puts 'Starting backfill of fit_tests.mask_modded column...'

    total = FitTest.where(mask_modded: nil).count
    puts "Found #{total} fit tests to backfill"

    updated = FitTest.where(mask_modded: nil).update_all(mask_modded: false)
    puts "Updated #{updated} fit tests to have mask_modded = false"

    puts 'Backfill complete!'
  end
end
