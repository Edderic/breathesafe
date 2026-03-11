# frozen_string_literal: true

module Admin
  class UsersController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def index
      per_page = [(params[:per_page] || 25).to_i, 100].min
      per_page = 25 if per_page <= 0
      page = (params[:page] || 1).to_i
      page = 1 if page <= 0

      users_query = User.where(deleted_at: nil).includes(:profile)
      users_query = users_query.where(id: parsed_ids) if parsed_ids.any?

      if params[:search].present?
        search = "%#{params[:search].to_s.strip}%"
        users_query = users_query.left_joins(:profile).where(
          'users.email ILIKE :search OR profiles.first_name ILIKE :search OR profiles.last_name ILIKE :search',
          search: search
        )
      end

      users_query = users_query.order(:id)
      total_count = users_query.count
      users = users_query.offset((page - 1) * per_page).limit(per_page)

      render json: {
        users: users.map { |user| user_payload(user) },
        total_count: total_count,
        page: page,
        per_page: per_page,
        messages: []
      }, status: :ok
    end

    private

    def parsed_ids
      @parsed_ids ||= params[:ids].to_s.split(',').map(&:strip).reject(&:blank?).map(&:to_i).uniq
    end

    def user_payload(user)
      {
        id: user.id,
        email: user.email,
        first_name: user.profile&.first_name,
        last_name: user.profile&.last_name
      }
    end

    def ensure_admin
      return if current_user&.admin?

      render json: { users: [], messages: ['Unauthorized.'] }, status: :forbidden
    end
  end
end
