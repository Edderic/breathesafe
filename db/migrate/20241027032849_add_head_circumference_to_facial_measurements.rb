# frozen_string_literal: true

class AddHeadCircumferenceToFacialMeasurements < ActiveRecord::Migration[7.0]
  def change
    add_column :facial_measurements, :head_circumference, :integer
  end
end
