class Mask < ApplicationRecord
  belongs_to :author, class_name: 'User'
  validates_presence_of :unique_internal_model_code
  validates_uniqueness_of :unique_internal_model_code
end

