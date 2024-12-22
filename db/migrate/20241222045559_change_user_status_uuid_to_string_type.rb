class ChangeUserStatusUuidToStringType < ActiveRecord::Migration[7.0]
  def change
    change_column(:user_statuses, :uuid, :string)
  end
end
