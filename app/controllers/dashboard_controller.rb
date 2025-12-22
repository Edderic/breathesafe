# frozen_string_literal: true

# Dashboard controller for displaying statistics
class DashboardController < ApplicationController
  skip_forgery_protection

  def stats
    stats = DashboardService.call

    # Convert all symbol keys to string keys for JSON
    stats_json = deep_stringify_keys(stats)

    Rails.logger.info "Dashboard stats JSON keys: #{stats_json.keys}"
    Rails.logger.info "Pass rates by mask count: #{stats_json['fit_tests']['pass_rates']['by_mask'].count}"

    respond_to do |format|
      format.json do
        render json: stats_json, status: :ok
      end
    end
  end

  private

  def deep_stringify_keys(hash)
    hash.deep_transform_keys(&:to_s)
  end
end
