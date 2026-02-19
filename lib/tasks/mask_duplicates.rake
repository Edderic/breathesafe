# frozen_string_literal: true

namespace :masks do
  namespace :duplicates do
    desc 'Flatten duplicate chains so each duplicate points directly to the root (dry-run by default)'
    task flatten: :environment do
      apply = ActiveModel::Type::Boolean.new.cast(ENV['APPLY'])

      user = nil
      if apply
        user = if ENV['ADMIN_ID'].present?
                 User.find_by(id: ENV['ADMIN_ID'].to_i)
               elsif ENV['ADMIN_EMAIL'].present?
                 User.find_by(email: ENV['ADMIN_EMAIL'])
               end

        unless user&.admin?
          puts 'ERROR: APPLY=true requires ADMIN_ID or ADMIN_EMAIL for an admin user'
          exit 1
        end
      end

      puts 'Mask duplicate chain flatten'
      puts "Mode: #{apply ? 'APPLY' : 'DRY-RUN'}"

      result = MaskDuplicateChainFlattener.call(
        apply: apply,
        user: user,
        notes_prefix: 'Rake masks:duplicates:flatten'
      )

      puts "Total duplicate rows: #{result[:total_duplicates]}"
      puts "Flatten candidates: #{result[:flatten_candidates]}"

      if result[:planned].any?
        puts "\nPlanned changes:"
        result[:planned].each do |entry|
          puts "  mask #{entry[:mask_id]}: #{entry[:current_duplicate_of]} -> #{entry[:canonical_root_id]}"
        end
      end

      if apply
        puts "\nApplied changes: #{result[:changed].size}"
        if result[:errors].any?
          puts "Errors: #{result[:errors].size}"
          result[:errors].each do |entry|
            puts "  mask #{entry[:mask_id]} error: #{entry[:error]}"
          end
          exit 1
        end
      else
        puts "\nDry-run complete. Re-run with APPLY=true and ADMIN_EMAIL=... to apply."
      end
    rescue MaskDuplicateChainFlattener::Error => e
      puts "ERROR: #{e.message}"
      exit 1
    end
  end
end
