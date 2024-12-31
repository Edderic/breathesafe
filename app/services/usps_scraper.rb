if defined?(Rails) && Rails.env.development?
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
          sleep 5
        end
      end

      if !success
        raise UnsuccessfulScrapeError.new(message)
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
      # Confirm Mapping & Import Labels
      try(lambda { driver.find_element(:css => '#formik-file-upload-continue-btn').click() }, 'file-upload-continue')
      buttons_text = driver.find_elements(:css => "button[type='button']").map{|x| x.text}
      buttons_text
      view_in_label_manager_index = buttons_text.find_index("View In Label Manager")
      view_in_label_manager_button = driver.find_elements(:css => "button[type='button']")[view_in_label_manager_index]
      view_in_label_manager_button.click

      driver.find_element(:css => "button#add-all-complete-to-cart-btn").click


      # Scrape the stuff to costs
      datetime_now = DateTime.now

      datetime_format = [
        datetime_now.year,
        datetime_now.month,
        datetime_now.day,
        datetime_now.hour,
        datetime_now.minute,
        datetime_now.second
      ].join('-')

      dict = {}
      text_rows = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      len_text_rows = text_rows.count

      text_rows.each.with_index do |row, index|
        if index == 0 && index >= len_text_rows - 1
          next
        end

        dict[row[2]] = {
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
      try(lambda {driver.find_element(:css => '#cc-button').click()}, '#cc-button')
      try(lambda {driver.find_element(:css => '#cns-agreement-close').click()}, '#cns-agreement-close')

      # Add all the labels
      # driver.find_element(:css => 'button[data-cy="Label-Actions"]').click()

      text_rows_cart = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      text_rows_cart = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      text_rows_cart

      text_rows_cart.each do |cart_row|
        dict[cart_row[2]]['label_number'] = cart_row[-1]
      end
      text_rows_cart

      text_rows_cart.each do |cart_row|
        dict[cart_row[2]]['label_number'] = cart_row[-1]
      end

      try(lambda {driver.find_element(:css => '#pp-button').click()}, '#pp-button')
      try(lambda {driver.find_element(:css => '#cns-agreement-close').click()}, '#cns-agreement-close')



      # After payment, save the data to note that purchase labels have been created
      driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
      text_rows = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}

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
        ]
        dict.each do |key, value|
          if value.key?('label_number')
            csv << value.map{|k,v| v}
          end
        end
      end


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
  end

  scraper = UspsScraper.new
  scraper.bulk_purchase_label
  debugger
else
  class UspsScraper
  end
end
