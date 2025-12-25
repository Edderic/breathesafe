# frozen_string_literal: true

class AddProcedureToFitTests < ActiveRecord::Migration[7.0]
  def change
    add_column :fit_tests, :procedure, :string
  end
end
