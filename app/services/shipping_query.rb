require 'csv'

class ShippingQuery
  def self.find_users_who_are_awaiting_shipping_label
    # Accepted users who do not yet have a purchase label?
    # TODO: find latest refresh datetime and use that
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
          SELECT *
          FROM user_statuses
          LEFT JOIN shipping_statuses ON user_statuses.uuid = shipping_statuses.to_user_uuid
          LEFT JOIN address_statuses ON user_statuses.address_uuid = address_statuses.uuid
          WHERE shipping_statuses.purchase_label = '{}'
        SQL
      ).to_json
    )
  end

  def self.usps_csv(shipping_date: nil)
    rows = self.find_users_who_are_awaiting_shipping_label

    ::CSV.open("usps_labels_to_create.csv", "wb") do |csv|
      csv << [
        "Reference ID",
        "Shipping Date",
        "Item Description",
        "Item Quantity",
        "Item Weight (lb)",
        "Item Weight (oz)",
        "Item Value",
        "HS Tariff #",
        "Country of Origin",
        "Sender First Name",
        "Sender Middle Initial",
        "Sender Last Name",
        "Sender Company/Org Name",
        "Sender Address Line 1",
        "Sender Address Line 2",
        "Sender Address Line 3",
        "Sender Address Town/City",
        "Sender State",
        "Sender Country",
        "Sender ZIP Code",
        "Sender Urbanization Code",
        "Ship From Another ZIP Code",
        "Sender Email",
        "Sender Cell Phone",
        "Recipient Country",
        "Recipient First Name",
        "Recipient Middle Initial",
        "Recipient Last Name",
        "Recipient Company/Org Name",
        "Recipient Address Line 1",
        "Recipient Address Line 2",
        "Recipient Address Line 3",
        "Recipient Address Town/City",
        "Recipient Province",
        "Recipient State",
        "Recipient ZIP Code",
        "Recipient Urbanization Code",
        "Recipient Phone",
        "Recipient Email",
        "Service Type",
        "Package Type",
        "Package Weight (lb)",
        "Package Weight (oz)",
        "Length",
        "Width",
        "Height",
        "Girth",
        "Insured Value",
        "Contents",
        "Contents Description",
        "Package Comments",
        "Customs Form Reference #",
        "License #",
        "Certificate #",
        "Invoice #",
      ]
      rows.each do |row|
        csv << self.row_generator(row: row, shipping_date: shipping_date)
      end
    end
  end

  def self.row_generator(
    row:,
    shipping_date:nil
  )
    if shipping_date.nil?
      shipping_date = DateTime.now
    end

    {
      'Reference ID' => 'MaskRecommender',
      'Shipping Date' => shipping_date,
      "Item Description" => 'Mask Research',
      "Item Quantity" => '',
      "Item Weight (lb)" => '3',
      "Item Weight (oz)" => '12.3',
      "Item Value" => '',
      "HS Tariff #" => '',
      "Country of Origin" => 'US',
      "Sender First Name" => 'Edderic',
      "Sender Middle Initial" => '',
      "Sender Last Name" => 'Ugaddan',
      "Sender Company/Org Name" => 'Breathesafe LLC',
      "Sender Address Line 1" => '138 Miller Ave.',
      "Sender Address Line 2" => '',
      "Sender Address Line 3" => '',
      "Sender Address Town/City" => 'Rumford',
      "Sender State" => 'RI',
      "Sender Country" => 'US',
      "Sender ZIP Code" => '02916',
      "Sender Urbanization Code" => '',
      "Ship From Another ZIP Code" => '',
      "Sender Email" => 'info@breathesafe.xyz',
      "Sender Cell Phone" => '9089170124',
      "Recipient Country" => row['country'],
      "Recipient First Name" => row['first_name'],
      "Recipient Middle Initial" => '',
      "Recipient Last Name" => row['last_name'],
      "Recipient Company/Org Name" => '',
      "Recipient Address Line 1" => row['address_line_1'],
      "Recipient Address Line 2" => row['address_line_2'],
      "Recipient Address Line 3" => row['address_line_3'],
      "Recipient Address Town/City" => row['town_city'],
      "Recipient Province" => '',
      "Recipient State" => row['state'],
      "Recipient ZIP Code" => row['zip_code'],
      "Recipient Urbanization Code" => '',
      "Recipient Phone" => '',
      "Recipient Email" => '',
      "Service Type" => 'USPS Ground Advantage',
      "Package Type" => 'Choose Your Own Box',
      "Package Weight (lb)" => '3',
      "Package Weight (oz)" => '12.3',
      "Length" => '',
      "Width" => '',
      "Height" => '',
      "Girth" => '',
      "Insured Value" => '120',
      "Contents" => '',
      "Contents Description" => '',
      "Package Comments" => '',
      "Customs Form Reference #" => '',
      "License #" => '',
      "Certificate #" => '',
      "Invoice #" => '',
    }.reduce([]) do |accum, (key, value)|
      accum << value

      accum
    end
  end

  def self.find_shipping_statuses_with_blank_purchase_labels(user_status_names:)
    # TODO
    # Assumes name is unique, first_name and last_name
    # Get the address_uuid
    # Find the latest shipping where address_uuid = to_address_uuid
    #
    names = user_status_names.map {|u| "'#{u}'"}.join(', ')
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH latest_datetimes AS (
          SELECT uuid, MAX(refresh_datetime) AS latest_datetime
          FROM user_statuses
          GROUP BY 1
        ), user_st AS (
          SELECT user_statuses.uuid AS email, * FROM latest_datetimes
          INNER JOIN user_statuses ON user_statuses.refresh_datetime = latest_datetimes.latest_datetime
            AND user_statuses.uuid = latest_datetimes.uuid
          WHERE user_statuses.first_name || ' ' || user_statuses.last_name IN (#{names})
        )

        SELECT shipping_statuses.uuid AS shipping_status_uuid, * FROM user_st
        LEFT JOIN shipping_statuses ON shipping_statuses.to_address_uuid = user_st.address_uuid
        WHERE purchase_label = '{}'

        SQL
      ).to_json
    )
  end

  def self.find_shipping_statuses(user_status_names:)
    # TODO
    # Assumes name is unique, first_name and last_name
    # Get the address_uuid
    # Find the latest shipping where address_uuid = to_address_uuid
    #
    names = user_status_names.map {|u| "'#{u}'"}.join(', ')
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH latest_datetimes AS (
          SELECT uuid, MAX(refresh_datetime) AS latest_datetime
          FROM user_statuses
          GROUP BY 1
        ), user_st AS (
          SELECT user_statuses.uuid AS email, * FROM latest_datetimes
          INNER JOIN user_statuses ON user_statuses.refresh_datetime = latest_datetimes.latest_datetime
            AND user_statuses.uuid = latest_datetimes.uuid
          WHERE user_statuses.first_name || ' ' || user_statuses.last_name IN (#{names})
        )

        SELECT shipping_statuses.uuid AS shipping_status_uuid, * FROM user_st
        LEFT JOIN shipping_statuses ON shipping_statuses.to_address_uuid = user_st.address_uuid
        SQL
      ).to_json
    )
  end
end

