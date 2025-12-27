# frozen_string_literal: true

class CreateMaskStates < ActiveRecord::Migration[7.0]
  def change
    create_table :mask_states do |t|
      t.references :mask, null: false, foreign_key: true, index: true

      # Snapshot of all mask fields at creation time
      t.string :unique_internal_model_code
      t.text :modifications
      t.jsonb :image_urls, default: []
      t.jsonb :author_ids, default: []
      t.jsonb :where_to_buy_urls, default: []
      t.string :strap_type
      t.float :mass_grams
      t.float :height_mm
      t.float :width_mm
      t.float :depth_mm
      t.boolean :has_gasket
      t.float :initial_cost_us_dollars
      t.jsonb :sources, default: []
      t.text :notes
      t.string :filter_type
      t.jsonb :filtration_efficiencies, default: []
      t.jsonb :breathability, default: {}
      t.string :style
      t.float :filter_change_cost_us_dollars
      t.string :age_range
      t.string :color
      t.boolean :has_exhalation_valve
      t.references :author, foreign_key: { to_table: :users }
      t.float :perimeter_mm
      t.jsonb :payable_datetimes, default: []
      t.jsonb :colors, default: []
      t.integer :duplicate_of
      t.references :brand, foreign_key: true
      t.references :bulk_fit_tests_import, foreign_key: true

      t.timestamps
    end

    add_index :mask_states, %i[mask_id created_at]
  end
end
