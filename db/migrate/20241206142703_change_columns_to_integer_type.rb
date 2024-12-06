class ChangeColumnsToIntegerType < ActiveRecord::Migration[7.0]
  def change
    change_column(
      :facial_measurements,
      :lower_face_length,
      "float USING CAST(NULLIF(lower_face_length, '') AS FLOAT)"
    )
  end
end
