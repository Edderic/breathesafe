# frozen_string_literal: true

FactoryBot.define do
  factory :profile do
    association :user
    measurement_system { 'metric' }
    first_name { Faker::Name.first_name }
    last_name { Faker::Name.last_name }
    height_meters { rand(1.4..2.0).round(2) }
    stride_length_meters { rand(0.6..0.8).round(2) }
    year_of_birth { rand(1950..2000) }
    race_ethnicity do
      ['American Indian or Alaskan Native', 'Asian / Pacific Islander', 'Black or African American', 'Hispanic',
       'White / Caucasian', 'Multiple ethnicity / Other', 'Prefer not to disclose'].sample
    end
    gender_and_sex do
      ['Cisgender male', 'Cisgender female', 'MTF transgender', 'FTM transgender', 'Intersex', 'Other',
       'Prefer not to disclose'].sample
    end

    trait :with_socials do
      socials do
        {
          'twitter' => Faker::Internet.username,
          'instagram' => Faker::Internet.username,
          'facebook' => Faker::Internet.username
        }
      end
    end

    trait :with_demographics do
      demographics do
        {
          'occupation' => Faker::Job.title,
          'education' => Faker::Educator.degree,
          'income_range' => ['$0-$25,000', '$25,001-$50,000', '$50,001-$75,000', '$75,001-$100,000', '$100,001+'].sample
        }
      end
    end

    trait :with_study_dates do
      study_start_datetime { Time.current }
      study_goal_end_datetime { 6.months.from_now }
    end

    trait :with_risk_data do
      num_positive_cases_last_seven_days { rand(0..100) }
      num_people_population { rand(1000..1_000_000) }
      uncounted_cases_multiplier { rand(1.0..3.0).round(2) }
    end
  end
end
