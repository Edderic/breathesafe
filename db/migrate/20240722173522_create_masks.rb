# frozen_string_literal: true

class CreateMasks < ActiveRecord::Migration[7.0]
  def change
    create_table :masks do |t|
      t.string :unique_internal_model_code
      t.json :modifications
      t.string :filter_type
      t.boolean :elastomeric
      t.string :image_urls, array: true, default: []
      t.integer :author_ids, array: true, default: []
      t.string :where_to_buy_urls, array: true, default: []

      t.timestamps
    end
  end
end
