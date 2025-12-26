# frozen_string_literal: true

class UsersController < ApplicationController
  def index
    if unauthorized?
      status = 401
      to_render = {
        users: [],
        messages: ['Unauthorized.']
      }
    else
      users = []
      messages = []

      if params[:email].present?
        user = User.find_by(email: params[:email])
        if user
          users = [{
            id: user.id,
            email: user.email,
            admin: user.admin
          }]
        else
          users = []
        end
      else
        messages = ['Email parameter is required.']
      end

      to_render = {
        users: users,
        messages: messages
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
