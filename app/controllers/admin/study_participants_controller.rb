# frozen_string_literal: true

module Admin
  class StudyParticipantsController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def index
      # Get base study participant data
      base_query = StudyParticipantStatus
                   .select(:participant_uuid, :created_at,
                           :finished_study_datetime, :removal_from_study,
                           :qualifications, :equipment)
                   .order(created_at: :desc)
                   .limit(1000) # Limit for performance

      # Calculate masks count for each participant
      # For each participant_uuid, find their user_id, then find all managed_users,
      # then count unique masks tested by those managed users
      participants_with_masks = base_query.map do |participant|
        masks_count = calculate_masks_count(participant.participant_uuid)
        participant.as_json.merge('masks_count' => masks_count)
      end

      render json: participants_with_masks
    end

    def remove_from_study
      participant_uuid = params[:participant_uuid]
      reason = params[:reason]

      if participant_uuid.blank? || reason.blank?
        render json: { error: 'participant_uuid and reason are required' }, status: :unprocessable_entity
        return
      end

      # Find the StudyParticipantStatus record
      participant = StudyParticipantStatus.find_by(participant_uuid: participant_uuid)

      unless participant
        render json: { error: 'Participant not found' }, status: :not_found
        return
      end

      # Update the removal_from_study field with timestamp and reason
      removal_data = {
        removed_at: Time.current.utc.iso8601,
        reason: reason,
        removed_by_admin_id: current_user.id
      }

      participant.update!(removal_from_study: removal_data)

      render json: { success: true, message: 'Participant removed from study' }
    rescue StandardError => e
      Rails.logger.error("Error removing participant from study: #{e.message}")
      render json: { error: 'Failed to remove participant from study' }, status: :internal_server_error
    end

    def finish_study
      participant_uuid = params[:participant_uuid]

      if participant_uuid.blank?
        render json: { error: 'participant_uuid is required' }, status: :unprocessable_entity
        return
      end

      # Find the StudyParticipantStatus record
      participant = StudyParticipantStatus.find_by(participant_uuid: participant_uuid)

      unless participant
        render json: { error: 'Participant not found' }, status: :not_found
        return
      end

      # Set the finished_study_datetime to current time
      participant.update!(finished_study_datetime: Time.current)

      render json: { success: true, message: 'Study marked as finished' }
    rescue StandardError => e
      Rails.logger.error("Error finishing study: #{e.message}")
      render json: { error: 'Failed to finish study' }, status: :internal_server_error
    end

    private

    def calculate_masks_count(participant_uuid)
      # participant_uuid is actually the user's email address
      # Find the user by email
      user = User.find_by(email: participant_uuid)
      return 0 unless user

      # Get all managed users for this user (where they are the manager)
      managed_user_ids = ManagedUser.where(manager_id: user.id).pluck(:managed_id)
      return 0 if managed_user_ids.empty?

      # For each managed user, count unique masks they've tested
      # Then sum across all managed users
      total_unique_masks = managed_user_ids.sum do |managed_id|
        FitTest.where(user_id: managed_id).distinct.count(:mask_id)
      end

      total_unique_masks
    end

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Unauthorized' }, status: :forbidden
    end
  end
end
