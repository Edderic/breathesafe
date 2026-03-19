# frozen_string_literal: true

class FitFamily < ApplicationRecord
  has_many :masks, dependent: :restrict_with_exception

  validates :name, presence: true
  validates :slug, presence: true, uniqueness: true
end
