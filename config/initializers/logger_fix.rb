# frozen_string_literal: true

# Fix for ActiveSupport LoggerThreadSafeLevel Logger constant issue
# This ensures Logger is properly available in ActiveSupport modules

require 'logger'

# Ensure Logger is available in ActiveSupport::LoggerThreadSafeLevel
module ActiveSupport
  module LoggerThreadSafeLevel
    # Make Logger constant available in this module
    Logger = ::Logger
  end
end
