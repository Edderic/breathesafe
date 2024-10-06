class RemoveNotNullConstraintForFacialMeasurementIdInFitTests < ActiveRecord::Migration[7.0]
  def up
    change_column_null :fit_tests, :facial_measurement_id, true
  end

  def down
    change_column_null :fit_tests, :facial_measurement_id, false
  end
end
