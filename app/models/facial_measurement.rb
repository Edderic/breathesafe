class FacialMeasurement < ApplicationRecord
  belongs_to :user

  def self.latest(user)
    facial_measurements = FacialMeasurement.where(user_id: user.id).order(:created_at)

    if facial_measurements.size > 0
      return facial_measurements.last
    else
      return nil
    end
  end
end
