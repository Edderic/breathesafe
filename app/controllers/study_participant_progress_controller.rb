# frozen_string_literal: true

# Display managed users scoped by manager
class StudyParticipantProgressController < ApplicationController
  def index
    if current_user.nil?
      to_render = {
        managed_users: [],
        messages: ['Please log in.']
      }
      status = 422
    else
      managed_users = ManagedUser.for_manager_id(manager_id: current_user.id)

      to_render = {
        managed_users: managed_users,
        messages: []
      }

      status = 200
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end
end
