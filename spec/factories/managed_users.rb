FactoryBot.define do
  factory :managed_user do
    association :manager, factory: :user
    association :managed, factory: :user
  end
end 