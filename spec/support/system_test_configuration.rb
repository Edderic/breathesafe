# frozen_string_literal: true

require 'capybara/rspec'
require 'selenium-webdriver'
require 'net/http'
require 'openssl'
require 'uri'

# Configure webdrivers to handle SSL issues
# Monkey-patch Net::HTTP to disable SSL verification for webdrivers downloads
# This addresses CRL (Certificate Revocation List) verification failures
# This must be done BEFORE requiring webdrivers

# Patch Net::HTTP to disable SSL verification for webdrivers-related connections
Net::HTTP.class_eval do
  unless method_defined?(:original_use_ssl=)
    alias_method :original_use_ssl=, :use_ssl=

    def use_ssl=(value)
      self.original_use_ssl = value

      # If SSL is enabled, check if this is a webdrivers-related connection
      return unless value

      # Check caller stack to see if webdrivers is making this request
      is_webdrivers_request = caller.any? { |line| line.include?('webdrivers') }

      # Also check the address if available
      host_match = @address && (
        @address.include?('chromedriver') ||
        @address.include?('googleapis.com') ||
        @address.include?('github.com') ||
        @address.include?('edgedriver') ||
        @address.include?('google.com')
      )

      return unless is_webdrivers_request || host_match

      @ssl_context ||= OpenSSL::SSL::SSLContext.new
      @ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
      @ssl_context.verify_callback = ->(_preverify_ok, _cert_store) { true }
      # Disable CRL checking
      @ssl_context.options |= OpenSSL::SSL::OP_NO_CRL_CHECK if defined?(OpenSSL::SSL::OP_NO_CRL_CHECK)
    end
  end

  # Also patch the start method to ensure SSL context is applied
  unless method_defined?(:original_start)
    alias_method :original_start, :start

    def start(&block)
      # Check if this is a webdrivers request before starting
      if use_ssl? && !@ssl_context
        is_webdrivers_request = caller.any? { |line| line.include?('webdrivers') }
        host_match = @address && (
          @address.include?('chromedriver') ||
          @address.include?('googleapis.com') ||
          @address.include?('github.com') ||
          @address.include?('edgedriver') ||
          @address.include?('google.com')
        )

        if is_webdrivers_request || host_match
          @ssl_context ||= OpenSSL::SSL::SSLContext.new
          @ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
          @ssl_context.verify_callback = ->(_preverify_ok, _cert_store) { true }
          # Disable CRL checking
          @ssl_context.options |= OpenSSL::SSL::OP_NO_CRL_CHECK if defined?(OpenSSL::SSL::OP_NO_CRL_CHECK)
        end
      end

      original_start(&block)
    end
  end
end

# Now require webdrivers after the monkey-patch
require 'webdrivers'

# Disable webdrivers in CI so Selenium Manager handles ChromeDriver.
Webdrivers.disable! if ENV['CI'] && Webdrivers.respond_to?(:disable!)

# With Selenium 4.x, we can use the built-in driver manager instead of webdrivers
# Disable webdrivers auto-update to let Selenium's driver manager handle ChromeDriver
# This avoids version lookup issues with newer Chrome versions
Webdrivers.install_dir = nil
Webdrivers.cache_time = 86_400

# Unset webdrivers' driver_path proc AFTER it's been set by webdrivers
# This allows Selenium 4.x's built-in driver manager to handle ChromeDriver automatically
if defined?(Selenium::WebDriver::Chrome::Service)
  # Clear the driver_path proc that webdrivers sets up
  # This allows Selenium 4.x's built-in driver manager to handle ChromeDriver automatically
  Selenium::WebDriver::Chrome::Service.driver_path = nil
end

# Also patch webdrivers update to be a no-op to prevent any download attempts
# Override the update method on Chromedriver's singleton class
if defined?(Webdrivers::Chromedriver)
  Webdrivers::Chromedriver.singleton_class.class_eval do
    # Redefine update method to skip webdrivers download
    # This overrides the inherited method from Common
    def update
      # Skip webdrivers update - let Selenium 4.x handle driver management
      # Create an instance to check if binary exists
      instance = new
      if instance.correct_binary?
        Webdrivers.logger.debug 'Using existing ChromeDriver binary'
        return instance.driver_path
      end

      # Return nil to let Selenium's driver manager handle it
      Webdrivers.logger.debug 'Letting Selenium handle ChromeDriver management'
      nil
    end
  end
end

# Patch webdrivers network module to use SSL verification disabled
if defined?(Webdrivers::Network)
  Webdrivers::Network.singleton_class.class_eval do
    unless method_defined?(:original_get_response)
      alias_method :original_get_response, :get_response

      def get_response(url, limit = 10)
        raise Webdrivers::ConnectionError, 'Too many HTTP redirects' if limit.zero?

        uri = URI(url)
        http_class = http
        http_instance = http_class.new(uri.host, uri.port)

        # Disable SSL verification for webdrivers downloads
        configure_ssl_for_webdrivers(http_instance) if uri.scheme == 'https'

        begin
          request = Net::HTTP::Get.new(uri)
          response = http_instance.start { |http| http.request(request) }
        rescue SocketError
          raise Webdrivers::ConnectionError, "Can not reach #{url}"
        end

        Webdrivers.logger.debug "Get response: #{response.inspect}"

        if response.is_a?(Net::HTTPRedirection)
          location = response['location']
          Webdrivers.logger.debug "Redirected to #{location}"
          get_response(location, limit - 1)
        else
          response
        end
      end

      def configure_ssl_for_webdrivers(http_instance)
        http_instance.use_ssl = true
        http_instance.verify_mode = OpenSSL::SSL::VERIFY_NONE
        ssl_context = http_instance.instance_variable_get(:@ssl_context)
        ssl_context ||= OpenSSL::SSL::SSLContext.new
        http_instance.instance_variable_set(:@ssl_context, ssl_context)
        ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
        ssl_context.verify_callback = ->(_preverify_ok, _cert_store) { true }
        return unless defined?(OpenSSL::SSL::OP_NO_CRL_CHECK)

        ssl_context.options |= OpenSSL::SSL::OP_NO_CRL_CHECK
      end
    end
  end
end

Capybara.default_driver = :selenium_chrome_headless
Capybara.javascript_driver = :selenium_chrome_headless
Capybara.default_max_wait_time = 1
Capybara.server_port = 3001
Capybara.app_host = 'http://localhost:3001'

Capybara.register_driver :selenium_chrome_headless do |app|
  options = Selenium::WebDriver::Chrome::Options.new
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--disable-gpu')
  options.add_argument('--window-size=1400,1400')
  options.add_argument('--disable-web-security')
  options.add_argument('--allow-running-insecure-content')

  # Use Selenium's built-in driver manager which handles ChromeDriver automatically
  # This works better with newer Chrome versions and avoids webdrivers version lookup issues
  # The driver manager will automatically download and manage the correct ChromeDriver version
  service = Selenium::WebDriver::Service.chrome
  Capybara::Selenium::Driver.new(
    app,
    browser: :chrome,
    options: options,
    service: service
  )
end

RSpec.configure do |config|
  config.before(:each, type: :system) do
    Capybara.reset_sessions!
  end
end
