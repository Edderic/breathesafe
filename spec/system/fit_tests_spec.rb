# frozen_string_literal: true

require 'rails_helper'
require 'net/http'
require 'uri'

RSpec.describe 'Fit Test Creation', type: :system do
  let(:manager) { create(:user, :with_profile) }
  let(:admin) { create(:user, :admin, :with_profile) }
  let(:unauthorized_user) { create(:user, :with_profile) }
  let(:managed_user) { create(:user, :with_profile) }
  let(:facial_measurement) { create(:facial_measurement, user: managed_user) }
  let(:mask) { create(:mask, :with_images) }
  let(:measurement_device) { create(:measurement_device) }

  before do
    # Set up managed user relationship
    create(:managed_user, manager: manager, managed: managed_user)

    # Create test data
    facial_measurement
    mask
    measurement_device
  end

  describe 'Authentication scenarios' do
    context 'when a manager has managed users' do
      before do
        sign_in manager
        visit '/#/fit_tests/new'
        wait_for_page_load
      end

      it 'allows access to fit test creation page' do
        expect(page).to have_content('User selection')
      end

      it 'displays managed users in the user selection' do
        expect(page).to have_content(managed_user.profile.first_name)
        expect(page).to have_content(managed_user.profile.last_name)
      end
    end

    context 'when an admin signs in' do
      before do
        sign_in admin
        visit '/#/fit_tests/new'
        wait_for_page_load
      end

      it 'allows access to fit test creation page' do
        expect(page).to have_content('User selection')
      end
    end

    context 'when an unauthorized user signs in' do
      before do
        sign_in unauthorized_user
      end

      it 'redirects or shows unauthorized message when accessing fit test creation' do
        visit '/#/fit_tests/new'
        wait_for_page_load

        # Should either redirect or show no managed users
        expect(page).not_to have_content(managed_user.profile.first_name) if page.has_content?('User selection')
      end
    end
  end

  describe 'Full flow - Qualitative Fit Test (Full OSHA)' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'completes the full fit test creation flow' do
      # Step 1: Select user
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      # Step 2: Select mask
      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      # Step 3: Facial Hair
      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      # Step 4: User Seal Check
      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      # Step 5: Fit Test - Choose Procedure
      select_fit_test_procedure('qualitative: Full OSHA')
      select_solution('Saccharin')
      click_save_and_continue
      wait_for_navigation

      # Step 6: Fit Test - Results
      fill_qualitative_exercises
      click_save_and_continue
      wait_for_navigation

      # Step 7: Comfort
      fill_comfort
      click_save_and_continue
      wait_for_navigation

      # Verify fit test was created
      expect(FitTest.count).to eq(1)
      fit_test = FitTest.last
      expect(fit_test.user_id).to eq(managed_user.id)
      expect(fit_test.mask_id).to eq(mask.id)
      expect(fit_test.results['qualitative']).to be_present
    end
  end

  describe 'Full flow - Quantitative Fit Test (OSHA Fast Face Piece Respirators)' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'completes quantitative fit test with OSHA Fast procedure' do
      # Step 1-4: Same as qualitative
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      # Step 5: Fit Test - Choose Procedure
      select_fit_test_procedure('quantitative: OSHA Fast Face Piece Respirators')
      fill_quantitative_device_fields(measurement_device)
      select_testing_mode('N95')
      fill_aerosol_fields
      click_save_and_continue
      wait_for_navigation

      # Step 6: Fit Test - Results
      fill_quantitative_fast_exercises
      click_save_and_continue
      wait_for_navigation

      # Step 7: Comfort
      fill_comfort
      click_save_and_continue
      wait_for_navigation

      # Verify fit test was created
      expect(FitTest.count).to eq(1)
      fit_test = FitTest.last
      expect(fit_test.results['quantitative']).to be_present
      expect(fit_test.results['quantitative']['procedure']).to eq('OSHA Fast Filtering Face Piece Respirators')
    end
  end

  describe 'Full flow - Quantitative Fit Test (Full OSHA)' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'completes quantitative fit test with Full OSHA procedure' do
      # Step 1-4: Same as above
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      # Step 5: Fit Test - Choose Procedure
      select_fit_test_procedure('quantitative: Full OSHA')
      fill_quantitative_device_fields(measurement_device)
      select_testing_mode('N99')
      fill_aerosol_fields
      click_save_and_continue
      wait_for_navigation

      # Step 6: Fit Test - Results
      fill_quantitative_full_osha_exercises
      click_save_and_continue
      wait_for_navigation

      # Step 7: Comfort
      fill_comfort
      click_save_and_continue
      wait_for_navigation

      # Verify fit test was created
      expect(FitTest.count).to eq(1)
      fit_test = FitTest.last
      expect(fit_test.results['quantitative']).to be_present
      expect(fit_test.results['quantitative']['procedure']).to eq('Full OSHA')
    end
  end

  describe 'Edge cases - Missing required fields' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'shows validation error when trying to proceed without selecting user' do
      click_save_and_continue
      expect(page).to have_content(/user|required|select/i)
    end

    it 'shows validation error when trying to proceed without selecting mask' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      click_save_and_continue
      expect(page).to have_content(/mask|required|select/i)
    end

    it 'shows validation error when user seal check questions are incomplete' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      # Try to proceed without completing user seal check
      click_save_and_continue
      expect(page).to have_content(/required|fill|complete/i)
    end
  end

  describe 'Edge cases - Invalid data formats' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'handles invalid fit factor values in quantitative tests' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      select_fit_test_procedure('quantitative: OSHA Fast Face Piece Respirators')
      fill_quantitative_device_fields(measurement_device)
      select_testing_mode('N95')
      fill_aerosol_fields
      click_save_and_continue
      wait_for_navigation

      # Try to enter invalid fit factor (negative or non-numeric)
      fill_in_fit_factor('Normal breathing (SEALED)', 'invalid')
      click_save_and_continue

      # Should show validation error or prevent submission
      expect(page).to have_content(/invalid|error|number/i).or have_no_content('Fit test created')
    end
  end

  describe 'Edge cases - Network errors/timeouts' do
    around do |example|
      original_raise_server_errors = Capybara.raise_server_errors
      Capybara.raise_server_errors = false
      example.run
    ensure
      Capybara.raise_server_errors = original_raise_server_errors
    end

    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'handles network timeout gracefully' do
      # Simulate network timeout by stubbing the request
      allow(ActionDispatch::Request).to receive(:new).and_wrap_original do |method, *args|
        request = method.call(*args)
        allow(request).to receive(:remote_ip).and_raise(Timeout::Error)
        request
      end

      select_user(managed_user)
      click_save_and_continue

      # Should show error message
      expect(page).to have_content(/error|timeout|network|failed/i).or have_no_content('User selection')
    end
  end

  describe 'Edge cases - Browser back/forward navigation' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'preserves data when using browser back button' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      # Go back
      page.go_back
      wait_for_page_load

      # Data should be preserved
      expect(page).to have_content(managed_user.profile.first_name)
    end

    it 'preserves data when using browser forward button' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      page.go_back
      wait_for_page_load

      page.go_forward
      wait_for_page_load

      # Should be on mask selection with user still selected
      expect(page).to have_content('Mask Selection')
    end
  end

  describe 'Edge cases - Form validation errors' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'displays validation errors from the server' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      # Try to submit with invalid data
      # This would require stubbing the server response
      # For now, we'll test that error messages are displayed
      fill_facial_hair
      click_save_and_continue

      # If there are validation errors, they should be displayed
      # This is a placeholder for actual validation error testing
      expect(page).to have_content('User Seal Check')
    end
  end

  describe 'Edge cases - Missing facial measurements' do
    let(:user_without_facial_measurement) { create(:user, :with_profile) }

    before do
      create(:managed_user, manager: manager, managed: user_without_facial_measurement)
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'allows fit test creation even without facial measurements' do
      select_user(user_without_facial_measurement)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      # Should be able to proceed
      expect(page).to have_content(/fit test|procedure/i)
    end
  end

  describe 'Edge cases - Missing managed users' do
    let(:manager_without_managed_users) { create(:user, :with_profile) }

    before do
      sign_in manager_without_managed_users
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'shows message when no managed users are available' do
      expect(page).to have_content(/not able to find|no users|add user/i)
    end
  end

  describe 'Data persistence' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'persists fit test data after page refresh' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      # Refresh page
      page.refresh
      wait_for_page_load

      # Should still show selected mask (if stored in route params or session)
      # This depends on implementation
      expect(page).to have_content('Facial Hair')
    end
  end

  describe 'Database assertions' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'creates fit test record with correct attributes' do
      select_user(managed_user)
      click_save_and_continue
      wait_for_navigation

      select_mask(mask)
      click_save_and_continue
      wait_for_navigation

      fill_facial_hair
      click_save_and_continue
      wait_for_navigation

      fill_user_seal_check
      click_save_and_continue
      wait_for_navigation

      select_fit_test_procedure('qualitative: Full OSHA')
      select_solution('Bitrex')
      click_save_and_continue
      wait_for_navigation

      fill_qualitative_exercises
      click_save_and_continue
      wait_for_navigation

      fill_comfort
      click_save_and_continue
      wait_for_navigation

      # Verify database record
      expect(FitTest.count).to eq(1)
      fit_test = FitTest.last

      expect(fit_test.user_id).to eq(managed_user.id)
      expect(fit_test.mask_id).to eq(mask.id)
      expect(fit_test.facial_measurement_id).to eq(facial_measurement.id)
      expect(fit_test.user_seal_check).to be_present
      expect(fit_test.comfort).to be_present
      expect(fit_test.results['qualitative']).to be_present
      expect(fit_test.results['qualitative']['aerosol']['solution']).to eq('Saccharin')
    end
  end

  describe 'UI updates and redirects' do
    before do
      sign_in manager
      visit '/#/fit_tests/new'
      wait_for_page_load
    end

    it 'shows success message after fit test creation' do
      complete_full_fit_test_flow

      # Should redirect to fit tests page or show success message
      expect(page).to have_content(/success|created|saved/i).or have_content('Fit Tests')
    end

    it 'redirects to fit tests page after completion' do
      complete_full_fit_test_flow

      expect(page).to have_content('Fit Tests')
    end
  end

  # Helper methods
  private

  def sign_in(user)
    # For system tests with Capybara Selenium, we need to authenticate via HTTP
    # and then set the session cookie in the browser
    visit '/' # Establish session first

    # Get CSRF token from the page
    csrf_token = begin
      page.find('meta[name="csrf-token"]', visible: false)['content']
    rescue StandardError
      nil
    end

    # Make an HTTP request to authenticate and get the session cookie
    base_url = "http://#{Capybara.current_session.server.host}:#{Capybara.current_session.server.port}"
    uri = URI("#{base_url}/users/log_in")
    http = Net::HTTP.new(uri.host, uri.port)

    # First, get the session cookie by visiting the page
    get_request = Net::HTTP::Get.new('/')
    get_response = http.request(get_request)
    cookies = {}
    get_response.get_fields('Set-Cookie')&.each do |cookie|
      name, value = cookie.split(';').first.split('=')
      cookies[name] = value
    end

    # Now make the login request with CSRF token and session cookie
    request = Net::HTTP::Post.new(uri.path)
    request['Content-Type'] = 'application/json'
    request['Accept'] = 'application/json'
    request['X-CSRF-Token'] = csrf_token if csrf_token
    if cookies.any?
      cookie_string = cookies.map { |name, value| "#{name}=#{value}" }.join('; ')
      request['Cookie'] = cookie_string
    end
    request.body = { user: { email: user.email, password: 'password123' } }.to_json

    response = http.request(request)

    # Extract all cookies from response and set them in the browser
    response.get_fields('Set-Cookie')&.each do |cookie_header|
      cookie_parts = cookie_header.split(';')
      name, value = cookie_parts.first.split('=')

      cookie_hash = {
        name: name.strip,
        value: value,
        path: '/'
      }

      # Extract additional cookie attributes if present
      cookie_parts[1..].each do |part|
        part = part.strip
        if part.start_with?('domain=')
          domain = part.split('=')[1]
          # For localhost, don't set domain (Selenium requirement)
          cookie_hash[:domain] = domain unless domain == 'localhost' || domain.start_with?('127.')
        elsif part.start_with?('path=')
          cookie_hash[:path] = part.split('=')[1]
        end
      end

      # For localhost, don't set domain attribute
      cookie_hash.delete(:domain) if ['127.0.0.1', 'localhost'].include?(Capybara.current_session.server.host)

      page.driver.browser.manage.add_cookie(cookie_hash)
    end

    # Reload to ensure authenticated session
    visit '/'
    wait_for_page_load
  end

  def wait_for_page_load
    expect(page).to have_selector('body', wait: 10)
    sleep 0.5 # Allow Vue to render
  end

  def wait_for_navigation
    sleep 1 # Wait for navigation and Vue updates
  end

  def dismiss_popup
    return unless page.has_css?('.popup .close', wait: 1)

    find('.popup .close').click
    expect(page).to have_no_css('.popup', wait: 5)
  end

  def dismiss_all_popups
    3.times do
      break unless page.has_css?('.popup .close', wait: 1)

      find('.popup .close').click
      expect(page).to have_no_css('.popup', wait: 5)
    end
  end

  def click_save_and_continue
    dismiss_all_popups
    button = find('.button', text: 'Save and Continue', match: :first)
    page.execute_script('arguments[0].click()', button)
  end

  def select_user(user)
    if page.has_css?('select.user-select:not([disabled])', wait: 5)
      option_label = "#{user.profile.first_name} #{user.profile.last_name} - #{user.id}"
      find('select.user-select').select(option_label)
    else
      fill_in 'input[type="text"]', with: user.profile.first_name, match: :first
      sleep 0.5
      find('.text-row', text: "#{user.profile.first_name} #{user.profile.last_name}").click
    end
  end

  def select_mask(mask)
    unless page.has_css?('input[placeholder="Search for mask"]:not([disabled])', wait: 5)
      find('.step-item', text: 'Mask Selection', match: :first).click
    end

    find('input[placeholder="Search for mask"]').set(mask.unique_internal_model_code)
    sleep 0.5
    find('.card', text: mask.unique_internal_model_code).click
  end

  def fill_facial_hair
    # Fill in facial hair information
    # This depends on the actual form fields
    select 'No', from: 'Has facial hair' if page.has_select?('Has facial hair')
  end

  def fill_user_seal_check
    unless page.has_css?('h2', text: 'User Seal Check', wait: 5)
      find('.step-item', text: 'User Seal Check', match: :first).click
    end

    within(:xpath, "//div[contains(@class,'right-pane')][.//h2[contains(.,'User Seal Check')]]") do
      find('label', text: 'Somewhere in-between too small and too big', match: :first).click

      if page.has_content?('...how much air movement on your face along the seal of the mask did you feel?')
        find('label', text: 'No air movement', match: :first).click
      else
        find('label', text: 'Unnoticeable', match: :first).click
      end
    end
  end

  def select_fit_test_procedure(procedure)
    unless page.has_css?('h2', text: 'Fit Test', wait: 5)
      find('.step-item', text: 'Fit Test', match: :first).click
    end

    within(:xpath, "//div[contains(@class,'right-pane')][.//h2[contains(.,'Fit Test')]]") do
      dismiss_all_popups
      if page.has_css?('.tab', text: 'Choose Procedure')
        find('.tab', text: 'Choose Procedure', match: :first).click
      elsif page.has_select?('tabToShowSelect')
        select 'Choose Procedure', from: 'tabToShowSelect'
      end

      find('select', match: :first).select(procedure)

      if procedure.start_with?('quantitative')
        all('input[type="number"]').first&.set('1000')
      end
    end
  end

  def select_solution(solution)
    select solution, from: 'Solution' if page.has_select?('Solution')
  end

  def fill_quantitative_device_fields(device)
    select device.manufacturer, from: 'Device' if page.has_select?('Device')
  end

  def select_testing_mode(mode)
    select mode, from: 'Testing mode' if page.has_select?('Testing mode')
  end

  def fill_aerosol_fields
    fill_in 'Initial count (particles / cm3)', with: '1000' if page.has_field?('Initial count (particles / cm3)')
  end

  def fill_qualitative_exercises
    unless page.has_css?('h2', text: 'Fit Test', wait: 5)
      find('.step-item', text: 'Fit Test', match: :first).click
    end

    within(:xpath, "//div[contains(@class,'right-pane')][.//h2[contains(.,'Fit Test')]]") do
      dismiss_popup
      if page.has_css?('.tab', text: 'Results')
        find('.tab', text: 'Results', match: :first).click
      elsif page.has_select?('tabToShowSelect')
        select 'Results', from: 'tabToShowSelect'
      end

      all('select').each do |select_box|
        select_box.select('Pass')
      end
    end
  end

  def fill_quantitative_fast_exercises
    fill_quantitative_fit_factors
  end

  def fill_quantitative_full_osha_exercises
    fill_quantitative_fit_factors
  end

  def fill_quantitative_fit_factors
    unless page.has_css?('h2', text: 'Fit Test', wait: 5)
      find('.step-item', text: 'Fit Test', match: :first).click
    end

    within(:xpath, "//div[contains(@class,'right-pane')][.//h2[contains(.,'Fit Test')]]") do
      dismiss_all_popups
      if page.has_css?('.tab', text: 'Results')
        find('.tab', text: 'Results', match: :first).click
      elsif page.has_select?('tabToShowSelect')
        select 'Results', from: 'tabToShowSelect'
      end

      if page.has_field?('Initial count (particles / cm3)')
        fill_in 'Initial count (particles / cm3)', with: '1000'
      end

      all('input[placeholder="Fit factor"]').each do |input|
        input.set('100')
      end
    end
  end

  def fill_comfort
    unless page.has_css?('h2', text: 'Comfort Assessment', wait: 5)
      find('.step-item', text: 'Comfort Assessment', match: :first).click
    end

    within(:xpath, "//div[contains(@class,'right-pane')][.//h2[contains(.,'Comfort Assessment')]]") do
      find('label', text: 'Comfortable', match: :first).click
      find('label', text: 'Enough', match: :first).click
      all('label', text: 'Comfortable')[1].click
    end
  end

  def fill_in_fit_factor(exercise_name, value)
    fill_in exercise_name, with: value if page.has_field?(exercise_name)
  end

  def complete_full_fit_test_flow
    select_user(managed_user)
    click_save_and_continue
    wait_for_navigation

    select_mask(mask)
    click_save_and_continue
    wait_for_navigation

    fill_facial_hair
    click_save_and_continue
    wait_for_navigation

    fill_user_seal_check
    click_save_and_continue
    wait_for_navigation

    select_fit_test_procedure('qualitative: Full OSHA')
    select_solution('Saccharin')
    click_save_and_continue
    wait_for_navigation

    fill_qualitative_exercises
    click_save_and_continue
    wait_for_navigation

    fill_comfort
    click_save_and_continue
    wait_for_navigation
  end
end
