# frozen_string_literal: true

class Brand < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  has_many :masks, dependent: :nullify
end
