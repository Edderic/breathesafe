# frozen_string_literal: true

# Helper module for tokenizing mask names
module MaskTokenizer
  # Split mask name into tokens
  def self.tokenize(unique_internal_model_code)
    return [] if unique_internal_model_code.blank?

    # Split by space, hyphen, em-dash, and comma
    tokens = unique_internal_model_code.split(/[\s\-—,\[\]()]+/)
    tokens.reject(&:blank?)
  end

  # Valid categories for token classification
  VALID_CATEGORIES = %w[
    brand
    model
    color
    style
    strap
    filter_type
    size
    misc
    valved
  ].freeze
end
