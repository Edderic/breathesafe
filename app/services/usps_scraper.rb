if defined?(Rails) && (Rails.env.development? || Rails.env.test?)
  require 'selenium-webdriver'
  require 'nokogiri'
  require 'capybara'
  require 'dotenv/load'
  require 'debug'
  require 'csv'

  class UspsScraper
    def initialize
    end

    def try(function, message, max_attempts=3)
      counter = 0
      success = false
      while counter < max_attempts
        puts("Counter: #{counter}, #{message}")
        begin
          function.call()
          success = true
          counter = max_attempts
        rescue Selenium::WebDriver::Error::WebDriverError => e
          counter += 1
          sleep 3
        end
      end

      if !success
        debugger
      end
    end

    def bulk_purchase_label
      driver = Selenium::WebDriver.for :chrome
      driver.navigate.to("https://cns.usps.com")
      sleep 5
      try(lambda { driver.find_element(:css => '#username').send_keys(ENV['USPS_USERNAME']) }, 'username')
      sleep 2
      try(lambda { driver.find_element(:css => '#password').send_keys(ENV['USPS_PASSWORD']) }, 'password')
      sleep 1
      try(lambda { driver.find_element(:css => '#btn-submit').click() }, 'submit')
      sleep 3
      try(lambda { driver.navigate.to("https://cnsb.usps.com") }, 'visit cnsb.usps.com')

      try(lambda { driver.navigate.to("https://cnsb.usps.com/file-upload/define-data") }, 'visit file upload')


      try(lambda { driver.find_element(:css => '#select-file-btn').click() }, 'select-file-btn')
      # Pick a file
      debugger

      try(lambda { driver.find_element(:css => '#formik-file-upload-continue-btn').click() }, 'file-upload-continue')
      try(lambda { driver.find_element(:css => '#file-upload-import-btn').click() }, 'file-upload-import-btn')

      debugger
      # Confirm Mapping & Import Labels
      try(lambda { driver.find_element(:css => '#formik-file-upload-continue-btn').click() }, 'file-upload-continue')
      buttons_text = driver.find_elements(:css => "button[type='button']").map{|x| x.text}
      buttons_text
      view_in_label_manager_index = buttons_text.find_index("View In Label Manager")
      debugger
      view_in_label_manager_button = driver.find_elements(:css => "button[type='button']")[view_in_label_manager_index]
      try(lambda { view_in_label_manager_button.click }, 'click View In Label Manager')

      driver.find_element(:css => "button#add-all-complete-to-cart-btn").click


      # Scrape the stuff to costs
      datetime_now = DateTime.now
      datetime_format = get_datetime_format(datetime_now)

      table_dict = {}
      text_rows = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      len_text_rows = text_rows.count

      text_rows.each.with_index do |row, index|
        if index == 0 && index >= len_text_rows - 1
          next
        end

        table_dict[row[2]] = {
          ship_date: row[1],
          name: row[2],
          address_line_1: row[3],
          address_line_2: row[4],
          memo: row[5],
          items: row[6],
          weight: row[9],
          value: row[10],
          cost: row[15],
        }
      end

      # TODO: add the labels
      debugger

      # Go to cart
      driver.navigate.to("https://cnsb.usps.com/cart")

      # Proceed to payment
      try(lambda {driver.find_element(:css => '#proceed-to-payment-btn').click()}, '#proceed-to-payment-btn')
      try(lambda {driver.find_element(:css => '#top-agreement .checkbox').click()}, '#top-agreement .checkbox')
      try(lambda {driver.find_element(:css => '#cc-button').click()}, 'click #cc-button')
      try(lambda {driver.find_element(:css => '#continueLink').click()}, 'click #continueLink')
      try(lambda {driver.find_element(:css => '#cns-agreement-close').click()}, 'click #cns-agreement-close')

      # Add all the labels
      # driver.find_element(:css => 'button[data-cy="Label-Actions"]').click()

      text_rows_cart = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      text_rows_cart

      text_rows_cart.each { |cart_row| table_dict[cart_row[2]]['label_number'] = cart_row[-1] }


      # After payment, save the data to note that purchase labels have been created
      text_rows = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      usps_labels_to_create = ::CSV.read("usps_labels_to_create.csv", headers: true).map(&:to_h)

      self.add_in_weight_and_dimensions(date_time_format, table_dict, usps_labels_to_create)


      # driver.navigate.to("https://www.shaws.com/")
      # Make sure to find nearesnt store
      # debugger
      # driver.find_element(:css => 'svg.svg-icon-Close').click()

      # driver.navigate.to("https://www.shaws.com/shop/search-results.html?q=onion")
      # driver.find_element(:css => 'button#openFulfillmentModalButton').click()
      # driver.find_element(:css => 'input[aria-labelledby="zipcode"]').send_keys("02916\n")
      # driver.find_elements(:css => '.caption a[role="button"]')[0].click()
      # debugger

      # driver.find_element(:css => '#skip-main-content').send_keys("onion\n")

      # driver.navigate.to("https://www.shaws.com/")
      # Visit
      # @session = Capybara.current_session
      # @session.driver.visit("https://cns.usps.com")

      # @driver = @session.driver
      # @browser = @driver.browser
      # @browser.methods
      # @browser.find_element('#username')
      # @browser.find_element('#password')
    end

    class << self
      def get_datetime_format(datetime: DateTime.now)
        [
          datetime.year,
          datetime.month,
          datetime.day,
          datetime.hour,
          datetime.minute,
          datetime.second
        ].join('-')
      end

      def add_in_weight_and_dimensions(
        datetime_format: ,
        table_dict:,
        usps_labels_to_create:
      )

        ::CSV.open("#{datetime_format}_usps_labels_created.csv", "wb") do |csv|
          csv << [
            'ship_date',
            'name',
            'address_line_1',
            'address_line_2',
            'memo',
            'method',
            'delivery_estimate',
            'weight',
            'value',
            'label_number',
            "length",
            "width",
            "height",
            "package_weight_lb",
            "package_weight_oz"
          ]
          table_dict.each do |key, value|
            if value.key?('label_number') || value.key?(:label_number)
              data = usps_labels_to_create.find{|r| "#{r['Recipient First Name']} #{r['Recipient Last Name']}" == value["name"]}
              cleaned_up_keys = data.reduce({}) do |accum, (k, v)|
                new_key = k.downcase().gsub(" ", "_").gsub("(", "").gsub(")", "")
                accum[new_key] = v
                accum
              end

              csv << cleaned_up_keys.merge(value)
            end
          end
        end
      end
    end
  end
else
  class UspsScraper
  end
end
