# frozen_string_literal: true

class AddStudyStartDatetimeStudyGoalEndDatetimeToProfiles < ActiveRecord::Migration[7.0]
  def change
    add_column :profiles, :study_start_datetime, :datetime
    add_column :profiles, :study_goal_end_datetime, :datetime
  end
end
