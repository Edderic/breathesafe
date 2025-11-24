# frozen_string_literal: true

require 'csv'

class BulkFitTestsImport < ApplicationRecord
  belongs_to :user
  has_many :masks, dependent: :destroy
  has_many :fit_tests, dependent: :destroy

  validates :source_name, presence: true
  validates :source_type, presence: true

  # Encrypt user_matching and import_data fields
  encrypts :user_matching
  encrypts :import_data

  # Status enum-like values
  STATUSES = %w[pending processing completed failed].freeze

  validates :status, inclusion: { in: STATUSES }
  validate :import_data_must_be_valid_csv, if: -> { import_data.present? }

  before_validation :set_default_user_matching, if: -> { user_matching.blank? }

  private

  def set_default_user_matching
    self.user_matching = '{}' if user_matching.blank?
  end

  def import_data_must_be_valid_csv
    return if import_data.blank?

    begin
      CSV.parse(import_data)
    rescue CSV::MalformedCSVError => e
      errors.add(:import_data, "is not valid CSV: #{e.message}")
    rescue StandardError => e
      errors.add(:import_data, "could not be parsed as CSV: #{e.message}")
    end
  end
end
