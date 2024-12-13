class CreateActions < ActiveRecord::Migration[7.0]
  def change
    create_table :actions do |t|
      t.datetime :datetime
      t.string :name
      t.string :type
      t.jsonb :metadata

      t.timestamps
    end
  end
end
