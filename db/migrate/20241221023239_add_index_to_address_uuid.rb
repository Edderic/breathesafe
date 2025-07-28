# frozen_string_literal: true

class AddIndexToAddressUuid < ActiveRecord::Migration[7.0]
  def change
    add_index :address_statuses, %i[uuid refresh_datetime], unique: true
  end
end
