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

  def self.missing_ratio_sql
    <<-SQL
        latest_facial_measurement_missing AS (
          SELECT *,
            CASE WHEN bitragion_subnasale_arc = 0 OR bitragion_subnasale_arc IS NULL THEN 1 ELSE 0 END AS bitragion_subnasale_arc_missing,
            CASE WHEN bitragion_menton_arc = 0 OR bitragion_menton_arc IS NULL THEN 1 ELSE 0 END AS bitragion_menton_arc_missing,
            CASE WHEN face_width = 0 OR face_width IS NULL THEN 1 ELSE 0 END AS face_width_missing,
            CASE WHEN face_length = 0 OR face_length IS NULL THEN 1 ELSE 0 END AS face_length_missing,
            CASE WHEN lower_face_length = 0 OR lower_face_length IS NULL THEN 1 ELSE 0 END AS lower_face_length_missing,
            CASE WHEN lip_width = 0 OR lip_width IS NULL THEN 1 ELSE 0 END AS lip_width_missing,
            CASE WHEN jaw_width = 0 OR jaw_width IS NULL THEN 1 ELSE 0 END AS jaw_width_missing,
            CASE WHEN nose_breadth = 0 OR nose_breadth IS NULL THEN 1 ELSE 0 END AS nose_breadth_missing,
            CASE WHEN nose_bridge_height = 0 OR nose_bridge_height IS NULL THEN 1 ELSE 0 END AS nose_bridge_height_missing,
            CASE WHEN nasal_root_breadth = 0 OR nasal_root_breadth IS NULL THEN 1 ELSE 0 END AS nasal_root_breadth_missing,
            CASE WHEN nose_protrusion = 0 OR nose_protrusion IS NULL THEN 1 ELSE 0 END AS nose_protrusion_missing,
            CASE WHEN head_circumference = 0 OR head_circumference IS NULL THEN 1 ELSE 0 END AS head_circumference_missing
          FROM latest_facial_measurements_for_users
        ), latest_facial_measurement_missing_counts AS (
          SELECT id,
            bitragion_subnasale_arc_missing +
            bitragion_menton_arc_missing +
            face_width_missing +
            face_length_missing +
            lower_face_length_missing +
            lip_width_missing +
            jaw_width_missing +
            nose_breadth_missing +
            nose_bridge_height_missing +
            nasal_root_breadth_missing +
            nose_protrusion_missing +
            head_circumference_missing AS missing_count

          FROM latest_facial_measurement_missing
        ), facial_measurement_missing_ratio AS (
          SELECT *, round(missing_count::numeric / 12, 4) AS missing_ratio
          FROM latest_facial_measurement_missing_counts
        )
    SQL
  end

end
