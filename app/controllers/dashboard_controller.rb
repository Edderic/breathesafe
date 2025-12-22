# frozen_string_literal: true

# Dashboard controller for displaying statistics
class DashboardController < ApplicationController
  skip_forgery_protection

  def stats
    stats = DashboardService.call

    respond_to do |format|
      format.json do
        render json: stats, status: :ok
      end
    end
  end
end
