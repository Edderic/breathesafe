require "test_helper"

class EventsControllerTest < ActionDispatch::IntegrationTest
  test "should get New" do
    get events_New_url
    assert_response :success
  end
end
