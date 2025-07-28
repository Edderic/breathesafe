# frozen_string_literal: true

class AddEventDisplayRiskTimeToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :event_display_risk_time, :string
  end
end
