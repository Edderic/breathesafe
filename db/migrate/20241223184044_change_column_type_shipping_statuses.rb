# frozen_string_literal: true

class ChangeColumnTypeShippingStatuses < ActiveRecord::Migration[7.0]
  def change
    change_column :shipping_statuses, :from_user_uuid, :string
    change_column :shipping_statuses, :to_user_uuid, :string
  end
end
