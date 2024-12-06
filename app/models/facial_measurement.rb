class FacialMeasurement < ApplicationRecord
  COLUMNS = [
    "face_width",
    "jaw_width",
    "face_depth",
    "face_length",
    "lower_face_length",
    "bitragion_menton_arc",
    "bitragion_subnasale_arc",
    # "cheek_fullness",
    "nasal_root_breadth",
    "nose_protrusion",
    "nose_bridge_height",
    "lip_width",
    "head_circumference",
  ]

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
