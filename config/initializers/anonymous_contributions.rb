# frozen_string_literal: true

require Rails.root.join('lib/anonymous_contribution_body_limit')
Rails.application.config.middleware.insert_before Rails::Rack::Logger, AnonymousContributionBodyLimit
Rails.application.config.filter_parameters += %i[contribution authorization credential credential_digest payload_digest]
