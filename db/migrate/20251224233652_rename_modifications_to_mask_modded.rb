# frozen_string_literal: true

class RenameModificationsToMaskModded < ActiveRecord::Migration[7.0]
  def change
    rename_column :fit_tests, :modifications, :mask_modded
  end
end
