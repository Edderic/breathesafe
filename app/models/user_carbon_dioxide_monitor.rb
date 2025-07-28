# frozen_string_literal: true

class UserCarbonDioxideMonitor < ApplicationRecord
  belongs_to :user, class_name: 'User'

  validates :serial, uniqueness: { scope: %i[model user_id], message: 'should be unique in the context of a model' }
end
