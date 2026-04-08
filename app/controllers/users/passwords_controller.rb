# frozen_string_literal: true

module Users
  class PasswordsController < Devise::PasswordsController
    private

    def after_sending_reset_password_instructions_path_for(_resource_name)
      '/#/signin'
    end

    def after_resetting_password_path_for(_resource)
      '/#/respirator_users'
    end
  end
end
