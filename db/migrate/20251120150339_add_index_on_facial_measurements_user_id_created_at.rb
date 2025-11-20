# frozen_string_literal: true

class AddIndexOnFacialMeasurementsUserIdCreatedAt < ActiveRecord::Migration[7.0]
  disable_ddl_transaction!

  def change
    add_index :facial_measurements,
              %i[user_id created_at],
              order: { created_at: :desc },
              algorithm: :concurrently,
              name: 'index_facial_measurements_on_user_id_and_created_at_desc'
  end
end
