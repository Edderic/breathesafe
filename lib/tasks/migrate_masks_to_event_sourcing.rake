# frozen_string_literal: true

namespace :masks do
  desc 'Migrate existing masks to event sourcing architecture'
  task migrate_to_event_sourcing: :environment do
    puts 'Starting migration of existing masks to event sourcing...'
    puts '-' * 80

    total_masks = Mask.count
    migrated_count = 0
    skipped_count = 0
    error_count = 0

    Mask.find_each.with_index do |mask, index|
      begin
        # Check if mask already has an initial state
        if mask.mask_states.exists?
          puts "  [#{index + 1}/#{total_masks}] Skipping mask #{mask.id} - already has initial state"
          skipped_count += 1
          next
        end

        # Create initial state snapshot
        mask.mask_states.create!(
          unique_internal_model_code: mask.unique_internal_model_code,
          modifications: mask.modifications,
          image_urls: mask.image_urls,
          author_ids: mask.author_ids,
          where_to_buy_urls: mask.where_to_buy_urls,
          strap_type: mask.strap_type,
          mass_grams: mask.mass_grams,
          height_mm: mask.height_mm,
          width_mm: mask.width_mm,
          depth_mm: mask.depth_mm,
          has_gasket: mask.has_gasket,
          initial_cost_us_dollars: mask.initial_cost_us_dollars,
          sources: mask.sources,
          notes: mask.notes,
          filter_type: mask.filter_type,
          filtration_efficiencies: mask.filtration_efficiencies,
          breathability: mask.breathability,
          style: mask.style,
          filter_change_cost_us_dollars: mask.filter_change_cost_us_dollars,
          age_range: mask.age_range,
          color: mask.color,
          has_exhalation_valve: mask.has_exhalation_valve,
          author_id: mask.author_id,
          perimeter_mm: mask.perimeter_mm,
          payable_datetimes: mask.payable_datetimes,
          colors: mask.colors,
          duplicate_of: mask.duplicate_of,
          brand_id: mask.brand_id,
          bulk_fit_tests_import_id: mask.bulk_fit_tests_import_id
        )

        puts "  ✓ [#{index + 1}/#{total_masks}] Migrated mask #{mask.id}: #{mask.unique_internal_model_code}"
        migrated_count += 1
      rescue StandardError => e
        puts "  ✗ [#{index + 1}/#{total_masks}] Error migrating mask #{mask.id}: #{e.message}"
        error_count += 1
      end
    end

    puts '-' * 80
    puts 'Migration Summary:'
    puts "  Total masks: #{total_masks}"
    puts "  Migrated: #{migrated_count}"
    puts "  Skipped (already migrated): #{skipped_count}"
    puts "  Errors: #{error_count}"
    puts '-' * 80
  end

  desc 'Migrate mask_breakdowns to mask_events'
  task migrate_breakdowns_to_events: :environment do
    puts 'Starting migration of mask_breakdowns to mask_events...'
    puts '-' * 80

    total_breakdowns = MaskBreakdown.count
    migrated_count = 0
    skipped_count = 0
    error_count = 0

    # Group breakdowns by mask_id to get the latest for each mask
    MaskBreakdown.order(:mask_id, :updated_at).find_each.with_index do |breakdown, index|
      begin
        # Check if this breakdown has already been migrated
        # (check if an event exists for this mask with the same breakdown data)
        existing_event = MaskEvent.where(
          mask_id: breakdown.mask_id,
          event_type: 'breakdown_updated'
        ).where("data->>'breakdown' = ?", breakdown.breakdown.to_json).exists?

        if existing_event
          puts "  [#{index + 1}/#{total_breakdowns}] Skipping breakdown #{breakdown.id} - already migrated"
          skipped_count += 1
          next
        end

        # Create a breakdown_updated event
        MaskEvent.create!(
          mask_id: breakdown.mask_id,
          user_id: breakdown.user_id,
          event_type: 'breakdown_updated',
          data: { breakdown: breakdown.breakdown },
          notes: breakdown.notes,
          created_at: breakdown.created_at,
          updated_at: breakdown.updated_at
        )

        puts "  ✓ [#{index + 1}/#{total_breakdowns}] Migrated breakdown #{breakdown.id} for mask #{breakdown.mask_id}"
        migrated_count += 1
      rescue StandardError => e
        puts "  ✗ [#{index + 1}/#{total_breakdowns}] Error migrating breakdown #{breakdown.id}: #{e.message}"
        error_count += 1
      end
    end

    puts '-' * 80
    puts 'Migration Summary:'
    puts "  Total breakdowns: #{total_breakdowns}"
    puts "  Migrated: #{migrated_count}"
    puts "  Skipped (already migrated): #{skipped_count}"
    puts "  Errors: #{error_count}"
    puts '-' * 80
  end

  desc 'Regenerate all mask states from events'
  task regenerate_all: :environment do
    puts 'Regenerating all mask states from events...'
    puts '-' * 80

    total_masks = Mask.count
    regenerated_count = 0
    error_count = 0

    Mask.find_each.with_index do |mask, index|
      begin
        mask.regenerate
        puts "  ✓ [#{index + 1}/#{total_masks}] Regenerated mask #{mask.id}"
        regenerated_count += 1
      rescue StandardError => e
        puts "  ✗ [#{index + 1}/#{total_masks}] Error regenerating mask #{mask.id}: #{e.message}"
        error_count += 1
      end
    end

    puts '-' * 80
    puts 'Regeneration Summary:'
    puts "  Total masks: #{total_masks}"
    puts "  Regenerated: #{regenerated_count}"
    puts "  Errors: #{error_count}"
    puts '-' * 80
  end
end
