# frozen_string_literal: true

namespace :consent do
  desc 'Fix users with invalid consent_form_version_accepted values (e.g., "{}")'
  task fix_invalid_versions: :environment do
    current_version = Rails.application.config.x.consent_form_version

    unless current_version.is_a?(String) && current_version.present?
      puts "ERROR: Invalid consent_form_version configured: #{current_version.inspect}"
      exit 1
    end

    puts "Current consent form version: #{current_version}"
    puts 'Searching for users with invalid consent_form_version_accepted values...'

    # Find users with invalid values
    invalid_users = User.where.not(consent_form_version_accepted: nil)
                        .where.not(consent_form_version_accepted: current_version)
                        .where("consent_form_version_accepted = '{}' OR consent_form_version_accepted = ''")

    puts "Found #{invalid_users.count} users with invalid consent_form_version_accepted values"

    if invalid_users.any?
      invalid_users.find_each do |user|
        puts "  - User ID #{user.id} (#{user.email}): #{user.consent_form_version_accepted.inspect}"
      end

      print "\nDo you want to fix these users? (y/n): "
      response = $stdin.gets.chomp.downcase

      if response == 'y'
        fixed_count = 0
        invalid_users.find_each do |user|
          old_value = user.consent_form_version_accepted
          # rubocop:disable Rails/SkipsModelValidations
          user.update_column(:consent_form_version_accepted, current_version)
          # rubocop:enable Rails/SkipsModelValidations
          puts "  ✓ Fixed User ID #{user.id}: #{old_value.inspect} -> #{current_version}"
          fixed_count += 1
        end
        puts "\nFixed #{fixed_count} users."
      else
        puts 'Aborted.'
      end
    else
      puts 'No users with invalid values found.'
    end
  end
end
