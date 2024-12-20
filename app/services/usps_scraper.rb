require 'selenium-webdriver'
require 'nokogiri'
require 'capybara'
require 'debug'
require 'dotenv/load'

class USPSScraper
  def initialize

    driver = Selenium::WebDriver.for :chrome
    # driver.navigate.to("https://cns.usps.com")
    # driver.find_element(:css => '#username').methods
    # driver.find_element(:css => '#username').send_keys(ENV['USPS_USERNAME'])
    # driver.find_element(:css => '#password').send_keys(ENV['USPS_PASSWORD'])
    # driver.find_element(:css => '#btn-submit').click()
    # driver.navigate.to("https://cnsb.usps.com")

    driver.navigate.to("https://www.shaws.com/")
    # Make sure to find nearesnt store
    debugger
    driver.find_element(:css => 'svg.svg-icon-Close').click()

    driver.navigate.to("https://www.shaws.com/shop/search-results.html?q=onion")
    driver.find_element(:css => 'button#openFulfillmentModalButton').click()
    driver.find_element(:css => 'input[aria-labelledby="zipcode"]').send_keys("02916\n")
    driver.find_elements(:css => '.caption a[role="button"]')[0].click()
    debugger

    driver.find_element(:css => '#skip-main-content').send_keys("onion\n")

    driver.navigate.to("https://www.shaws.com/")
    # Visit
    @session = Capybara.current_session
    @session.driver.visit("https://cns.usps.com")

    @driver = @session.driver
    @browser = @driver.browser
    @browser.methods
    @browser.find_element('#username')
    @browser.find_element('#password')
    debugger
  end
end

scraper = USPSScraper.new
scraper.methods
debugger
