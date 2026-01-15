# frozen_string_literal: true

require_relative 'boot'

require 'logger'
require 'rails/all'
# Ensure PostGIS adapter is loaded
require 'activerecord-postgis-adapter'

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module Breathesafe
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 7.0

    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments, which are processed later.
    #
    # config.time_zone = "Central Time (US & Canada)"
    # config.eager_load_paths << Rails.root.join("extras")

    # Configure encryption
    encryption_creds = Rails.application.credentials.encryption || {}
    encryption_primary = ENV['ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY']
    encryption_salt = ENV['ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT']
    encryption_deterministic = ENV['ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY']

    config.active_record.encryption.primary_key = encryption_primary || encryption_creds[:primary_key]
    config.active_record.encryption.key_derivation_salt = encryption_salt || encryption_creds[:key_derivation_salt]
    config.active_record.encryption.deterministic_key = encryption_deterministic || encryption_creds[:primary_key]

    if (Rails.env.test? || ENV['CI'].present?) &&
       (config.active_record.encryption.primary_key.nil? ||
        config.active_record.encryption.key_derivation_salt.nil? ||
        config.active_record.encryption.deterministic_key.nil?)
      fallback_key = '0' * 32
      fallback_salt = '1' * 32
      config.active_record.encryption.primary_key ||= fallback_key
      config.active_record.encryption.key_derivation_salt ||= fallback_salt
      config.active_record.encryption.deterministic_key ||= fallback_key
    end

    # Enable encryption
    config.active_record.encryption.extend_queries = true

    # Temporarily support unencrypted data during transition period
    config.active_record.encryption.support_unencrypted_data = true
  end
end
