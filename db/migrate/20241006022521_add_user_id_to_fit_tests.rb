class AddUserIdToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_reference :fit_tests, :user, foreign_key: true
  end
end
