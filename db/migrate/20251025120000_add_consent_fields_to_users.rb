# frozen_string_literal: true

class AddConsentFieldsToUsers < ActiveRecord::Migration[7.0]
  def change
    change_table :users, bulk: true do |t|
      t.string :consent_form_version_accepted
      t.datetime :consent_form_accepted_at
    end
  end
end
