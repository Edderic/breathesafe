# frozen_string_literal: true

namespace :users do
  desc 'Soft-delete a user account. Usage: rake users:delete_account USER_ID=123 CONFIRM=123'
  task delete_account: :environment do
    user_id = ENV.fetch('USER_ID', nil).to_i
    confirmation = ENV.fetch('CONFIRM', nil).to_i

    abort 'Usage: rake users:delete_account USER_ID=123 CONFIRM=123' unless user_id.positive?
    abort "CONFIRM must match USER_ID (#{user_id})" unless confirmation == user_id

    user = User.with_deleted.find_by(id: user_id)
    abort "User #{user_id} not found" unless user
    abort "User #{user_id} is already deleted" if user.deleted?

    puts "Preparing to delete user #{user.id} (#{user.email})"
    puts "  Profile: #{user.profile.present? ? 1 : 0}"
    puts "  Facial measurements: #{user.facial_measurements.count}"
    puts "  Fit tests: #{FitTest.where(user_id: user.id).count}"
    puts "  Bulk fit test imports: #{user.bulk_fit_tests_imports.count}"
    puts "  Addresses: #{Address.where(user_id: user.id).count}"
    puts "  Measurement devices: #{user.measurement_devices.count}"
    puts "  Carbon dioxide monitor links: #{user.user_carbon_dioxide_monitors.count}"
    puts "  Managed users: #{ManagedUser.where(manager_id: user.id).count}"
    puts "  Authored masks preserved: #{user.masks.count}"

    user.soft_delete!

    puts "Deleted user #{user.id}. Anonymized email: #{User.with_deleted.find(user.id).email}"
  end
end
