class CreateMasks < ActiveRecord::Migration[7.0]
  def change
    create_table :masks do |t|
      t.string :unique_internal_model_code
      t.json :modifications
      t.string :type
      t.string :image_urls
      t.string :where_to_buy_urls

      t.timestamps
    end
  end
end
