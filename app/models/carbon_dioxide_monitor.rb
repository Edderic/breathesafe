# frozen_string_literal: true

class CarbonDioxideMonitor < ApplicationRecord
  has_many :users, through: :user_carbon_dioxide_monitors

  validates :serial, uniqueness: { scope: :model, message: 'should be unique in the context of a model' }
end
