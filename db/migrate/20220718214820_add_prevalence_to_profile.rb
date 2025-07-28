# frozen_string_literal: true

class AddPrevalenceToProfile < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :num_positive_cases_last_seven_days, :integer
    add_column :profiles, :num_people_population, :integer
    add_column :profiles, :uncounted_cases_multiplier, :float
  end
end
