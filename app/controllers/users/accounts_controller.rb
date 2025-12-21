# frozen_string_literal: true

module Users
  # Controller for account deletion
  class AccountsController < ApplicationController
    skip_before_action :verify_authenticity_token

    def destroy
      if current_user.nil?
        status = 401
        messages = ['Please log in.']
      else
        begin
          current_user.soft_delete!

          # Sign out the user
          sign_out current_user

          status = 200
          messages = ['Account deleted successfully.']
        rescue StandardError => e
          Rails.logger.error("Failed to delete account for user #{current_user.id}: #{e.message}")
          Rails.logger.error(e.backtrace.join("\n"))

          status = 500
          messages = ["Failed to delete account: #{e.message}"]
        end
      end

      to_render = {
        messages: messages
      }

      respond_to do |format|
        format.json do
          render json: to_render.to_json, status: status
        end
      end
    end
  end
end
