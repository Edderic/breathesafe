# frozen_string_literal: true

class AnonymousContributionExportsController < ApplicationController
  def index
    return render json: { error: 'Unauthorized' }, status: :unauthorized unless current_user
    return render json: { error: 'Forbidden' }, status: :forbidden unless current_user.admin?

    rows = AnonymousContribution.where('id > ?', params[:after_id].to_i).order(:id).limit(500).to_a
    response.headers['Cache-Control'] = 'no-store'
    render json: {
      contributions: rows.map do |row|
        row.attributes.slice('id', 'contribution_id', 'anonymous_participant_id', 'measurement_version',
                             'measurements', 'fit_tests', 'consent_version', 'consent_accepted_at')
      end,
      next_after_id: rows.size == 500 ? rows.last.id : nil
    }
  end
end
