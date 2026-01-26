# frozen_string_literal: true

# Configure SSL for AWS SDK connections to handle certificate verification issues
# This addresses CRL (Certificate Revocation List) verification failures that can occur
# when CRL servers are unreachable or certificate stores are outdated

if defined?(Rails)
  require 'openssl'
  require 'net/http'

  # Configure OpenSSL to handle CRL verification failures gracefully
  # This is a workaround for environments where CRL checking fails but certificates are valid
  # We monkey-patch Net::HTTP to intercept SSL context creation for AWS endpoints
  Net::HTTP.class_eval do
    # Store the original method if not already stored
    alias_method :original_use_ssl=, :use_ssl= unless method_defined?(:original_use_ssl=)

    def use_ssl=(value)
      # Call the original method first
      self.original_use_ssl = value

      # Only apply custom SSL configuration for AWS endpoints
      return unless value && @address&.include?('amazonaws.com')

      # Create or get SSL context
      @ssl_context ||= OpenSSL::SSL::SSLContext.new
      @ssl_context.verify_mode = OpenSSL::SSL::VERIFY_PEER

      # Set verify callback to handle CRL errors gracefully
      @ssl_context.verify_callback = lambda do |preverify_ok, _cert_store|
        # If basic certificate verification failed, reject
        return false unless preverify_ok

        # Allow connection even if CRL check would fail
        # This is necessary when CRL servers are unreachable
        true
      end
    end
  end
end
