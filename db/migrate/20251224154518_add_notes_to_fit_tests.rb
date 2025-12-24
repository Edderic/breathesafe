# frozen_string_literal: true

class AddNotesToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_column :fit_tests, :notes, :text

    # Add check constraint for practical limit (10,000 chars)
    reversible do |dir|
      dir.up do
        execute <<-SQL
          ALTER TABLE fit_tests
          ADD CONSTRAINT notes_length_check
          CHECK (length(notes) <= 10000);
        SQL
      end

      dir.down do
        execute <<-SQL
          ALTER TABLE fit_tests
          DROP CONSTRAINT notes_length_check;
        SQL
      end
    end
  end
end
