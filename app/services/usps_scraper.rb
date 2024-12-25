require 'selenium-webdriver'
require 'nokogiri'
require 'capybara'
require 'dotenv/load'
require 'csv'

class USPSScraper
  def initialize

    driver = Selenium::WebDriver.for :chrome
    driver.navigate.to("https://cns.usps.com")
    driver.find_element(:css => '#username').send_keys(ENV['USPS_USERNAME'])
    driver.find_element(:css => '#password').send_keys(ENV['USPS_PASSWORD'])
    driver.find_element(:css => '#btn-submit').click()
    driver.navigate.to("https://cnsb.usps.com")

    debugger

    driver.find_element(:css => '#file-upload-btn').click()
    sleep 3
    driver.find_element(:css => '#file-upload-btn').click()
    sleep 3
    driver.find_element(:css => '#select-file-btn').click()
    debugger
    driver.find_element(:css => '#formik-file-upload-continue-btn').click()
    driver.find_element(:css => '#file-upload-import-btn').click()
    # Confirm Mapping & Import Labels
    driver.find_element(:css => '#formik-file-upload-continue-btn').click()
    sleep 5
    driver.find_element(:css => '#formik-file-upload-continue-btn').click()
    driver.find_element(:css => "button[type='button']").click()
    driver.find_element(:xpath => "//[contains(text(), 'View in Label Manager')]").click()

    rows[0].text.split("\n")
    rows[0].find_element('td[aria-label="recipient-info"]').text
    rows[0].methods
    rows[0].find_elements('td')


    # Add all the labels
    driver.find_element(:css => 'th[aria-label="checkbox-all-labels"]').click()
    # Proceed to payment
    #
    driver.find_element(:css => '#proceed-to-payment-btn').click()
    driver.find_element(:css => '#top-agreement .checkbox').click()
    driver.find_element(:css => '#pp-button').click()
    driver.find_element(:css => '#cns-agreement-close').click()



    # After payment, save the data to note that purchase labels have been created
    driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}
    text_rows = driver.find_elements(:css => "tbody tr").map{|r| r.text.split("\n")}

    datetime_now = DateTime.now
    datetime_format = [
      datetime_now.year,
      datetime_now.month,
      datetime_now.day,
      datetime_now.hour,
      datetime_now.minute,
      datetime_now.second
    ].join('-')
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
      text_rows.each do |r|
        csv << [
          r[1],
          r[2],
          r[3],
          r[4],
          r[5],
          r[6],
          r[7],
          r[8],
          r[10],
          r[12]
        ]
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

scraper = USPSScraper.new
scraper.methods
debugger
