# frozen_string_literal: true

FactoryBot.define do
  factory :mask do
    sequence(:unique_internal_model_code) { |n| "MASK-#{n}" }
    modifications { {} }
    image_urls { [] }
    author_ids { [] }
    where_to_buy_urls { [] }
    strap_type { 'Elastic' }
    mass_grams { '50' }
    height_mm { '100' }
    width_mm { '150' }
    depth_mm { '50' }
    has_gasket { false }
    initial_cost_us_dollars { 10.0 }
    sources { [] }
    notes { 'Test mask' }
    filter_type { 'N95' }
    filtration_efficiencies { [] }
    breathability { [] }
    style { 'Duckbill' }
    filter_change_cost_us_dollars { 5.0 }
    age_range { 'Adult' }
    color { 'White' }
    has_exhalation_valve { false }
    association :author, factory: :user
    perimeter_mm { 300.0 }
    payable_datetimes { [] }
    colors { [] }

    trait :with_filtration_efficiency do
      filtration_efficiencies do
        [
          {
            filtration_efficiency_percent: 99.9,
            filtration_efficiency_notes: 'Aaron test',
            filtration_efficiency_source: 'https://example.com'
          }
        ]
      end
    end

    trait :with_breathability do
      breathability do
        [
          {
            pressure_drop: 2.5,
            flow_rate: 85,
            source: 'https://example.com'
          }
        ]
      end
    end

    trait :with_images do
      image_urls { ['https://example.com/mask1.jpg', 'https://example.com/mask2.jpg'] }
    end

    trait :with_sources do
      sources { ['https://example.com/source1', 'https://example.com/source2'] }
    end

    trait :with_where_to_buy do
      where_to_buy_urls { ['https://example.com/buy1', 'https://example.com/buy2'] }
    end

    trait :with_payable_datetimes do
      payable_datetimes do
        [
          {
            start_datetime: Time.current,
            end_datetime: 1.month.from_now
          }
        ]
      end
    end

    trait :with_colors do
      colors { %w[White Black Blue] }
    end
  end

  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    password { 'password123' }
    password_confirmation { 'password123' }
    confirmed_at { Time.current }
    admin { false }
    # Set consent fields by default so test users don't see consent form
    consent_form_version_accepted do
      version = Rails.application.config.x.consent_form_version
      version = nil if version == '{}' || version.blank?
      version || 'v1'
    end
    consent_form_accepted_at { Time.current }

    trait :unconfirmed do
      confirmed_at { nil }
      confirmation_sent_at { Time.current }
    end

    trait :locked do
      locked_at { Time.current }
      failed_attempts { 5 }
    end

    trait :admin do
      admin { true }
    end

    trait :with_reset_password do
      reset_password_token { SecureRandom.hex(20) }
      reset_password_sent_at { Time.current }
    end

    trait :with_unlock_token do
      unlock_token { SecureRandom.hex(20) }
    end

    trait :with_profile do
      after(:create) do |user|
        create(:profile, user: user)
      end
    end

    trait :with_facial_measurements do
      after(:create) do |user|
        create(:facial_measurement, user: user)
      end
    end

    trait :with_fit_tests do
      after(:create) do |user|
        create_list(:fit_test, 2, user: user)
      end
    end

    trait :with_managed_users do
      after(:create) do |user|
        create_list(:managed_user, 2, manager: user)
      end
    end

    trait :with_measurement_devices do
      after(:create) do |user|
        create_list(:measurement_device, 2, owner: user)
      end
    end

    trait :with_carbon_dioxide_monitors do
      after(:create) do |user|
        create_list(:user_carbon_dioxide_monitor, 2, user: user)
      end
    end

    trait :with_addresses do
      after(:create) do |user|
        create_list(:address, 2, user: user)
      end
    end

    trait :without_consent do
      consent_form_version_accepted { nil }
      consent_form_accepted_at { nil }
    end
  end

  factory :facial_measurement do
    association :user
    source { 'digital_caliper' }
    face_width { rand(120..160) }
    jaw_width { rand(100..140) }
    face_depth { rand(80..120) }
    face_length { rand(180..220) }
    lower_face_length { rand(60..80) }
    bitragion_menton_arc { rand(300..350) }
    bitragion_subnasale_arc { rand(250..300) }
    cheek_fullness { 'medium' }
    nasal_root_breadth { rand(15..25) }
    nose_protrusion { rand(15..25) }
    nose_bridge_height { rand(10..20) }
    lip_width { rand(40..60) }
    head_circumference { rand(500..600) }
    nose_breadth { rand(30..40) }

    trait :complete do
      # All measurements are already set by default
    end

    trait :incomplete do
      face_width { nil }
      jaw_width { nil }
      face_depth { nil }
      face_length { nil }
      lower_face_length { nil }
      bitragion_menton_arc { nil }
      bitragion_subnasale_arc { nil }
      nasal_root_breadth { nil }
      nose_protrusion { nil }
      nose_bridge_height { nil }
      lip_width { nil }
      head_circumference { nil }
      nose_breadth { nil }
    end

    trait :with_zero_values do
      face_width { 0 }
      jaw_width { 0 }
      face_depth { 0 }
      face_length { 0 }
      lower_face_length { 0 }
      bitragion_menton_arc { 0 }
      bitragion_subnasale_arc { 0 }
      nasal_root_breadth { 0 }
      nose_protrusion { 0 }
      nose_bridge_height { 0 }
      lip_width { 0 }
      head_circumference { 0 }
      nose_breadth { 0 }
    end

    trait :with_minimum_values do
      face_width { 120 }
      jaw_width { 100 }
      face_depth { 80 }
      face_length { 180 }
      lower_face_length { 60 }
      bitragion_menton_arc { 300 }
      bitragion_subnasale_arc { 250 }
      nasal_root_breadth { 15 }
      nose_protrusion { 15 }
      nose_bridge_height { 10 }
      lip_width { 40 }
      head_circumference { 500 }
      nose_breadth { 30 }
    end

    trait :with_maximum_values do
      face_width { 160 }
      jaw_width { 140 }
      face_depth { 120 }
      face_length { 220 }
      lower_face_length { 80 }
      bitragion_menton_arc { 350 }
      bitragion_subnasale_arc { 300 }
      nasal_root_breadth { 25 }
      nose_protrusion { 25 }
      nose_bridge_height { 20 }
      lip_width { 60 }
      head_circumference { 600 }
      nose_breadth { 40 }
    end

    trait :with_cheek_fullness do
      cheek_fullness { %w[low medium high].sample }
    end
  end

  factory :fit_test do
    association :user
    association :mask
    association :facial_measurement
    association :quantitative_fit_testing_device, factory: :measurement_device, strategy: :build

    user_seal_check do
      {
        'sizing' => {
          'What do you think about the sizing of this mask relative to your face?' => 'Too small'
        },
        'negative' => {
          '...how much air passed between your face and the mask?' => nil
        },
        'positive' => {
          '...how much did your glasses fog up?' => 'A lot',
          '...how much pressure build up was there?' => 'No pressure build up',
          '...how much air movement on your face along the seal of the mask did you feel?' => 'A lot of air movement'
        }
      }
    end

    comfort do
      {
        'rating' => 4,
        'notes' => 'Comfortable fit'
      }
    end

    facial_hair do
      {
        'has_facial_hair' => false,
        'notes' => 'Clean shaven'
      }
    end

    results do
      {
        'quantitative' => {
          'testing_mode' => 'N99',
          'exercises' => [
            {
              'name' => 'Normal breathing (SEALED)',
              'fit_factor' => 200
            },
            {
              'name' => 'Deep breathing',
              'fit_factor' => 150
            },
            {
              'name' => 'Talking',
              'fit_factor' => 100
            }
          ]
        }
      }
    end

    trait :with_n95_mode do
      results do
        {
          'quantitative' => {
            'testing_mode' => 'N95',
            'exercises' => [
              {
                'name' => 'Normal breathing (SEALED)',
                'fit_factor' => 100
              },
              {
                'name' => 'Deep breathing',
                'fit_factor' => 75
              },
              {
                'name' => 'Talking',
                'fit_factor' => 50
              }
            ]
          }
        }
      end
    end

    trait :with_too_small_mask do
      user_seal_check do
        {
          'sizing' => {
            'What do you think about the sizing of this mask relative to your face?' => 'Too small'
          },
          'negative' => {
            '...how much air passed between your face and the mask?' => nil
          },
          'positive' => {
            '...how much did your glasses fog up?' => 'A lot',
            '...how much pressure build up was there?' => 'No pressure build up',
            '...how much air movement on your face along the seal of the mask did you feel?' => 'A lot of air movement'
          }
        }
      end
    end

    trait :with_just_right_mask do
      user_seal_check do
        {
          'sizing' => {
            'What do you think about the sizing of this mask relative to your face?' => \
            'Somewhere in-between too small and too big'
          },
          'negative' => {
            '...how much air passed between your face and the mask?' => nil
          },
          'positive' => {
            '...how much did your glasses fog up?' => 'Not at all',
            '...how much pressure build up was there?' => 'As expected',
            '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
          }
        }
      end
    end
    trait :with_too_large_mask do
      user_seal_check do
        {
          'sizing' => {
            'What do you think about the sizing of this mask relative to your face?' => 'Too big'
          },
          'negative' => {
            '...how much air passed between your face and the mask?' => nil
          },
          'positive' => {
            '...how much did your glasses fog up?' => 'A lot',
            '...how much pressure build up was there?' => 'No pressure build up',
            '...how much air movement on your face along the seal of the mask did you feel?' => 'A lot of air movement'
          }
        }
      end
    end

    trait :with_low_comfort do
      comfort do
        {
          'rating' => 2,
          'notes' => 'Uncomfortable fit'
        }
      end
    end

    trait :with_facial_hair do
      facial_hair do
        {
          'has_facial_hair' => true,
          'notes' => 'Has beard'
        }
      end
    end

    trait :with_custom_exercises do
      results do
        {
          'quantitative' => {
            'testing_mode' => 'N99',
            'exercises' => [
              {
                'name' => 'Normal breathing (SEALED)',
                'fit_factor' => 250
              },
              {
                'name' => 'Deep breathing',
                'fit_factor' => 200
              },
              {
                'name' => 'Talking',
                'fit_factor' => 150
              },
              {
                'name' => 'Head movements',
                'fit_factor' => 180
              }
            ]
          }
        }
      end
    end

    trait :with_failed_fit_factors do
      results do
        {
          'quantitative' => {
            'testing_mode' => 'N99',
            'exercises' => [
              {
                'name' => 'Normal breathing (SEALED)',
                'fit_factor' => 50
              },
              {
                'name' => 'Deep breathing',
                'fit_factor' => 30
              },
              {
                'name' => 'Talking',
                'fit_factor' => 20
              }
            ]
          }
        }
      end
    end

    trait :without_quantitative_device do
      quantitative_fit_testing_device_id { nil }
    end

    trait :without_facial_measurement do
      facial_measurement { nil }
    end

    trait :without_mask do
      mask { nil }
    end
  end

  factory :mask_pair do
    association :mask_a, factory: :mask
    association :mask_b, factory: :mask
    name_distance { 0.5 }
    history { [] }
  end

  factory :measurement_device do
    association :owner, factory: :user
    measurement_device_type { 'quantitative_fit_testing' }
    manufacturer { 'TSI' }
    model { 'PortaCount Pro+' }
    sequence(:serial) { |n| "SN#{n}" }
    notes { 'Test device' }
    remove_from_service { false }

    trait :removed_from_service do
      remove_from_service { true }
    end

    trait :with_notes do
      notes { "Device calibrated on #{Time.current.strftime('%Y-%m-%d')}" }
    end

    trait :with_fit_tests do
      after(:create) do |device|
        create_list(:fit_test, 2, quantitative_fit_testing_device: device)
      end
    end

    trait :digital_caliper do
      measurement_device_type { 'digital_caliper' }
      manufacturer { 'Mitutoyo' }
      model { '500-196-30' }
    end

    trait :tape_measure do
      measurement_device_type { 'tape_measure' }
      manufacturer { 'Stanley' }
      model { 'PowerLock' }
    end

    trait :carbon_dioxide_monitor do
      measurement_device_type { 'carbon_dioxide_monitor' }
      manufacturer { 'CO2Meter' }
      model { 'AZ-0004' }
    end

    trait :nebulizer do
      measurement_device_type { 'nebulizer' }
      manufacturer { 'TSI' }
      model { '8026' }
    end

    trait :hood do
      measurement_device_type { 'hood' }
      manufacturer { 'TSI' }
      model { '8025' }
    end

    trait :solution do
      measurement_device_type { 'solution' }
      manufacturer { 'TSI' }
      model { '8038' }
    end
  end
end
