Feature: API integration

  Scenario: Health endpoint returns status ok
    When I GET "/health/"
    Then the response status code should be 200
    And the response JSON should have "status" with value "ok"

  Scenario: Journey endpoint with valid request
    When I POST "/v1/journey/" with JSON:
      """
      {
        "station_codes": ["AAA", "BBB"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30
      }
      """
    Then the response status code should be 200
    And the response JSON should have "arrival_time"

  Scenario: Journey endpoint with invalid request
    When I POST "/v1/journey/" with JSON:
      """
      {
        "station_codes": ["AAA"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30
      }
      """
    Then the response status code should be 422
    And the response JSON should have "detail"
