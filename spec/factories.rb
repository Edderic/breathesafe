FactoryBot.define do
  factory :mask do
    sequence(:unique_internal_model_code) { |n| "MASK-#{n}" }
    modifications { {} }
    image_urls { [] }
    author_ids { [] }
    where_to_buy_urls { [] }
    strap_type { "Elastic" }
    mass_grams { "50" }
    height_mm { "100" }
    width_mm { "150" }
    depth_mm { "50" }
    has_gasket { false }
    initial_cost_us_dollars { 10.0 }
    sources { [] }
    notes { "Test mask" }
    filter_type { "N95" }
    filtration_efficiencies { [] }
    breathability { [] }
    style { "Duckbill" }
    filter_change_cost_us_dollars { 5.0 }
    age_range { "Adult" }
    color { "White" }
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
            filtration_efficiency_notes: "Aaron test",
            filtration_efficiency_source: "https://example.com"
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
            source: "https://example.com"
          }
        ]
      end
    end

    trait :with_images do
      image_urls { ["https://example.com/mask1.jpg", "https://example.com/mask2.jpg"] }
    end

    trait :with_sources do
      sources { ["https://example.com/source1", "https://example.com/source2"] }
    end

    trait :with_where_to_buy do
      where_to_buy_urls { ["https://example.com/buy1", "https://example.com/buy2"] }
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
      colors { ["White", "Black", "Blue"] }
    end
  end
end 