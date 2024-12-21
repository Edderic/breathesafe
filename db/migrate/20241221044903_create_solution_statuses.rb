class CreateSolutionStatuses < ActiveRecord::Migration[7.0]
  def change
    create_table :solution_statuses do |t|
      t.uuid :uuid, null: false
      t.datetime :refresh_datetime, null: false
      t.string :model, null: false
      t.jsonb :flavor_type, null: false
      t.jsonb :how
      t.jsonb :cost
      t.jsonb :volume
      t.string :concentration_type
      t.float :volume_level_proportion

      t.timestamps
    end

    add_index :solution_statuses, [:uuid, :refresh_datetime], unique: true
    add_index :solution_statuses, :uuid
  end
end
