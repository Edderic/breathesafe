# frozen_string_literal: true

class BackfillMaskColorsFromColor < ActiveRecord::Migration[7.0]
  def up
    backfill_table(:masks)
    backfill_table(:mask_states)
  end

  def down
    # no-op: keep colors data as-is
  end

  private

  def backfill_table(table_name)
    execute <<~SQL
      UPDATE #{table_name}
      SET colors = CASE
        WHEN colors IS NULL OR jsonb_typeof(colors) <> 'array' THEN to_jsonb(ARRAY[color]::text[])
        WHEN colors @> to_jsonb(ARRAY[color]::text[]) THEN colors
        ELSE colors || to_jsonb(ARRAY[color]::text[])
      END
      WHERE color IS NOT NULL
        AND btrim(color) <> '';
    SQL
  end
end
