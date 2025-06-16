Feature: Journey planning logic

  Scenario: Wait time at a station exceeds max_wait
    Given a JourneyRequest payload with station_codes ["AAA", "BBB", "CCC"], start_time "2025-06-16T10:00:00", max_wait 5
    When I simulate a journey with a long wait at BBB
    Then a journey planning error should be raised containing "Wait time at BBB exceeds max_wait"

  Scenario: No trains found for a leg
    Given a JourneyRequest payload with station_codes ["AAA", "ZZZ"], start_time "2025-06-16T10:00:00", max_wait 30
    When I simulate a journey with no trains for a leg
    Then a journey planning error should be raised containing "No trains found from AAA to ZZZ"

  Scenario: Successful multi-leg journey
    Given a JourneyRequest payload with station_codes ["AAA", "BBB", "CCC"], start_time "2025-06-16T10:00:00", max_wait 30
    When I simulate a successful multi-leg journey
    Then the journey should return an arrival time in ISO 8601 format
