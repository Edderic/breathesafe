# frozen_string_literal: true

class AddMeasurementSourceToAnonymousContributions < ActiveRecord::Migration[7.0]
  def change
    add_column :anonymous_contributions, :measurement_source_contribution_id, :uuid
    add_index :anonymous_contributions, :measurement_source_contribution_id, name: 'index_anonymous_measurement_source'
    add_foreign_key :anonymous_contributions, :anonymous_contributions,
                    column: :measurement_source_contribution_id, primary_key: :contribution_id
  end
end
