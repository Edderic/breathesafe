# frozen_string_literal: true

module Admin
  class StudyParticipantsController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def index
      @study_participants = StudyParticipantStatus
                            .select(:participant_uuid, :created_at,
                                    :finished_study_datetime, :removal_from_study,
                                    :qualifications, :equipment)
                            .order(created_at: :desc)
                            .limit(1000) # Limit for performance

      render json: @study_participants
    end

    private

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Unauthorized' }, status: :forbidden
    end
  end
end
