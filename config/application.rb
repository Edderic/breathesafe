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
    config.active_record.encryption.primary_key = Rails.application.credentials.encryption[:primary_key]
    config.active_record.encryption.key_derivation_salt = Rails.application.credentials.encryption[:key_derivation_salt]
    config.active_record.encryption.deterministic_key = Rails.application.credentials.encryption[:primary_key]

    # Enable encryption
    config.active_record.encryption.extend_queries = true
  end
end
