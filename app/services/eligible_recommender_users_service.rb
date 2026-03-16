# frozen_string_literal: true

class EligibleRecommenderUsersService
  def self.call(viewer:)
    new(viewer:).call
  end

  def initialize(viewer:)
    @viewer = viewer
  end

  def call
    return [] unless viewer

    eligible_users = candidate_users.filter_map do |user|
      begin
        LatestRecommenderFacialMeasurementsService.call(viewer: viewer, recommender_user_id: user.id)
      rescue LatestRecommenderFacialMeasurementsService::MissingMeasurementsError,
             LatestRecommenderFacialMeasurementsService::ForbiddenError,
             ActiveRecord::RecordNotFound
        next
      end

      {
        managed_id: user.id,
        full_name: full_name_for(user)
      }
    end

    eligible_users.sort_by { |row| row[:full_name].to_s.downcase }
  end

  private

  attr_reader :viewer

  def candidate_users
    ids = if viewer.admin?
            ManagedUser.distinct.pluck(:managed_id)
          else
            ManagedUser.where(manager_id: viewer.id).distinct.pluck(:managed_id)
          end

    User.includes(:profile).where(id: ids)
  end

  def full_name_for(user)
    profile = user.profile
    full_name = [profile&.first_name, profile&.last_name].compact.join(' ').strip
    return full_name if full_name.present?

    user.email
  end
end
