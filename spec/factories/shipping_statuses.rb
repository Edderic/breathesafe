# frozen_string_literal: true

FactoryBot.define do
  factory :shipping_status do
    uuid { SecureRandom.uuid }
    refresh_datetime { Time.current }
    to_user_uuid { Faker::Internet.email }
    from_user_uuid { Faker::Internet.email }
    from_address_uuid { SecureRandom.uuid }
    to_address_uuid { SecureRandom.uuid }
  end
end
