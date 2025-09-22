# frozen_string_literal: true

ENV['BUNDLE_GEMFILE'] ||= File.expand_path('../Gemfile', __dir__)

require 'bundler/setup' # Set up gems listed in the Gemfile.

# Fix for Logger constant issue in ActiveSupport
require 'logger'

require 'bootsnap/setup' # Speed up boot time by caching expensive operations.
