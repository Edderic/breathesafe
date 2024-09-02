class MeasurementDevice < ApplicationRecord
  belongs_to :owner_id

  def self.viewable(user)
    self.where(owner_id: user.id)
  end
end
