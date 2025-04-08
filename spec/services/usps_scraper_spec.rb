require 'rails_helper'
require 'csv'

describe UspsScraper do
  describe "add_in_weight_and_dimensions" do

    let(:table_dict) do
      {
        "Some One" => {
          'ship_date' => "2025-01-01",
          'name'=> "Some One",
          'address_line_1' => '1600 Pennsylvania Ave.',
          'address_line_2' => 'XYZ',
          'memo' => 'Ref#: MaskRecommender',
          'method' => 'Ref#: MaskRecommender,USPS Ground Advantage® Custom Packaging',
          'delivery_estimate' => "ABC",
          'weight' => '60.3 oz',
          'value' => "EFG",
          'label_number' => "123456789",
        },
        "Another One" => {
          'ship_date' => "2025-01-01",
          'name'=> "Another One",
          'address_line_1' => '543 Pennsylvania Ave.',
          'address_line_2' => 'XYZ',
          'memo' => 'Ref#: MaskRecommender',
          'method' => 'Ref#: MaskRecommender,USPS Ground Advantage® Custom Packaging',
          'delivery_estimate' => "ABC",
          'weight' => '60.3 oz',
          'value' => "EFG",
          'label_number' => "987654321",
        }
      }.with_indifferent_access
    end

    let(:usps_labels_to_create) do
      [
        {
          'Recipient First Name' => "Another",
          'Recipient Last Name' => "One",
          'Length' => "40",
          'Width' => "50",
          'Height' => "60",
          'Package Weight (lb)' => '4',
          'Package Weight (oz)' => '5',
        },
        {
          'Recipient First Name' => "Some",
          'Recipient Last Name' => "One",
          'Length' => "10",
          'Width' => "20",
          'Height' => "30",
          'Package Weight (lb)' => '2',
          'Package Weight (oz)' => '3',
        }
      ]
    end

    let(:expected_insert_1) do
      {
        "address_line_1"=>"543 Pennsylvania Ave.",
        "address_line_2"=>"XYZ",
        "delivery_estimate"=>"ABC",
        "height"=>"60",
        "label_number"=>"987654321",
        "length"=>"40",
        "memo"=>"Ref#: MaskRecommender",
        "method"=>"Ref#: MaskRecommender,USPS Ground Advantage® Custom Packaging",
        "name"=>"Another One",
        "package_weight_lb"=>"4",
        "package_weight_oz"=>"5",
        "recipient_first_name"=>"Another",
        "recipient_last_name"=>"One",
        "ship_date"=>"2025-01-01",
        "value"=>"EFG",
        "weight"=>"60.3 oz",
        "width"=>"50"
      }
    end

    let(:expected_insert_2) do
      {
        "address_line_1"=>"1600 Pennsylvania Ave.",
        "address_line_2"=>"XYZ",
        "delivery_estimate"=>"ABC",
        "height"=>"30",
        "label_number"=>"123456789",
        "length"=>"10",
        "memo"=>"Ref#: MaskRecommender",
        "method"=>"Ref#: MaskRecommender,USPS Ground Advantage® Custom Packaging",
        "name"=>"Some One",
        "package_weight_lb"=>"2",
        "package_weight_oz"=>"3",
        "recipient_first_name"=>"Some",
        "recipient_last_name"=>"One",
        "ship_date"=>"2025-01-01",
        "value"=>"EFG",
        "weight"=>"60.3 oz",
        "width"=>"20"
      }
    end

    let(:csv_object) do
      []
    end

    let(:datetime_format) do
      UspsScraper.get_datetime_format(datetime: DateTime.now)
    end

    let(:headers) do
      [
        "ship_date",
        "name",
        "address_line_1",
        "address_line_2",
        "memo",
        "method",
        "delivery_estimate",
        "weight",
        "value",
        "label_number",
        "length",
        "width",
        "height",
        "package_weight_lb",
        "package_weight_oz"
      ]
    end

    before(:each) do
      allow(CSV).to receive(:open).with("#{datetime_format}_usps_labels_created.csv", "wb").and_yield(csv_object)
      allow(csv_object).to receive(:<<).with(expected_insert_1)
      allow(csv_object).to receive(:<<).with(expected_insert_2)
      allow(csv_object).to receive(:<<).with(headers)
    end

    it "should insert a row with length, width, height, etc." do
      UspsScraper.add_in_weight_and_dimensions(
        datetime_format: datetime_format,
        table_dict: table_dict,
        usps_labels_to_create: usps_labels_to_create
      )
      expect(csv_object).to have_received(:<<).with(expected_insert_1)
    end

    it "should insert another row with length, width, height, etc." do
      UspsScraper.add_in_weight_and_dimensions(
        datetime_format: datetime_format,
        table_dict: table_dict,
        usps_labels_to_create: usps_labels_to_create
      )
      expect(csv_object).to have_received(:<<).with(expected_insert_1)
    end
  end
end
