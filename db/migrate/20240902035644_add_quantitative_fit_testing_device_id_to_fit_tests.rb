# frozen_string_literal: true

class AddQuantitativeFitTestingDeviceIdToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_reference :fit_tests, :quantitative_fit_testing_device, foreign_key: { to_table: :measurement_devices }
  end
end
