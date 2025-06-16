Feature: Real journey planning with TransportAPI

  Scenario: Plan a real journey with earliest arrivals for each leg using the live TransportAPI
    Given a start time of "2025-06-04T07:00:00+01:00"
    And max_wait is 400
    When I POST to the journey API with station codes ["LBG", "SAJ", "NWX", "BXY"]
    Then the response status code should be 200
    And the response JSON should have "arrival_time"
