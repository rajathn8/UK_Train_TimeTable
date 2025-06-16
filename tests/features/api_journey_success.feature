Feature: Journey planning API - successful multi-leg journey

  Scenario: Plan a journey with earliest arrivals for each leg
    Given the following train legs:
      | from | to  | departs | arrives |
      | LBG  | SAJ | 07:19   | 07:28   |
      | SAJ  | NWX | 07:32   | 07:34   |
      | NWX  | BXY | 07:45   | 08:11   |
    And a start time of "2025-06-04T07:00:00+01:00"
    And max_wait is 400
    When I POST to the journey API with station codes ["LBG", "SAJ", "NWX", "BXY"]
    Then the response status code should be 200
    And the response JSON should have "arrival_time" with value "2025-06-04T08:11:00+01:00"
