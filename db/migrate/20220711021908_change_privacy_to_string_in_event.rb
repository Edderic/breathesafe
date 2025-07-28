# frozen_string_literal: true

class ChangePrivacyToStringInEvent < ActiveRecord::Migration[7.0]
  def change
    change_column :events, :private, :string
  end
end
