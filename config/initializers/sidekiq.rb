# frozen_string_literal: true

redis_url = ENV['REDIS_URL'] || ENV['REDIS_TLS_URL']

return if redis_url.blank?

redis_options = { url: redis_url }
if redis_url.start_with?('rediss://')
  redis_options[:ssl] = true
  redis_options[:ssl_params] = { verify_mode: OpenSSL::SSL::VERIFY_NONE }
end

Sidekiq.configure_server do |config|
  config.redis = redis_options
end

Sidekiq.configure_client do |config|
  config.redis = redis_options
end
