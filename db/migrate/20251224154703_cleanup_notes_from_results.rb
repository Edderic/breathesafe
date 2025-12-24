# frozen_string_literal: true

class CleanupNotesFromResults < ActiveRecord::Migration[7.0]
  def up
    # This migration removes the 'notes' field from results.qualitative and results.quantitative
    # Run this after confirming the notes column migration is successful

    Rails.logger.debug 'Cleaning up notes from results JSONB...'

    FitTest.find_each do |fit_test|
      next unless fit_test.results.is_a?(Hash)

      modified = false

      if fit_test.results['qualitative'].is_a?(Hash) && fit_test.results['qualitative'].key?('notes')
        fit_test.results['qualitative'].delete('notes')
        modified = true
      end

      if fit_test.results['quantitative'].is_a?(Hash) && fit_test.results['quantitative'].key?('notes')
        fit_test.results['quantitative'].delete('notes')
        modified = true
      end

      if modified
        fit_test.update_column(:results, fit_test.results)
        Rails.logger.debug "Cleaned up FitTest ##{fit_test.id}"
      end
    end

    Rails.logger.debug 'Cleanup complete!'
  end

  def down
    # Cannot restore deleted notes - they should be in the notes column
    Rails.logger.debug 'Cannot restore notes to results JSONB. They are in the notes column.'
  end
end
