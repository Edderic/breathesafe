# frozen_string_literal: true

class CreateFitFamiliesAndBackfillMasks < ActiveRecord::Migration[7.0]
  class MigrationMask < ApplicationRecord
    self.table_name = 'masks'
  end

  class MigrationFitFamily < ApplicationRecord
    self.table_name = 'fit_families'
  end

  def up
    create_table :fit_families do |t|
      t.string :name, null: false
      t.string :slug, null: false

      t.timestamps
    end

    add_index :fit_families, :slug, unique: true
    add_reference :masks, :fit_family, foreign_key: true, index: true, null: true

    say_with_time 'Backfilling fit families for existing masks' do
      MigrationMask.reset_column_information
      MigrationFitFamily.reset_column_information

      MigrationMask.find_each do |mask|
        fit_family = MigrationFitFamily.create!(
          name: mask.unique_internal_model_code.presence || "Mask #{mask.id}",
          slug: "mask-#{mask.id}"
        )
        mask.update!(fit_family_id: fit_family.id)
      end
    end

    change_column_null :masks, :fit_family_id, false
  end

  def down
    remove_reference :masks, :fit_family, foreign_key: true, index: true
    drop_table :fit_families
  end
end
