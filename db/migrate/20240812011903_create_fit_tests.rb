class CreateFitTests < ActiveRecord::Migration[7.0]
  def change
    create_table :fit_tests do |t|
      t.references :mask, null: false, foreign_key: true
      t.jsonb :user_seal_check
      t.jsonb :comfort
      t.jsonb :facial_hair
      t.jsonb :protection_factors

      t.timestamps
    end
  end
end
