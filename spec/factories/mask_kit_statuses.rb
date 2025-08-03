# frozen_string_literal: true

FactoryBot.define do
  factory :mask_kit_status do
    uuid { SecureRandom.uuid }
    mask_uuid { rand(1..1000) }
    refresh_datetime { Time.current }
  end
end 