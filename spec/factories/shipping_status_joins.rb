# frozen_string_literal: true

FactoryBot.define do
  factory :shipping_status_join do
    refresh_datetime { Time.current }
    shippable_type { 'MaskKitStatus' }
    shipping_uuid { SecureRandom.uuid }
    shippable_uuid { SecureRandom.uuid }
  end
end 