Feature: JourneyRequest schema validation

  Scenario: Station codes list is too short
    Given a JourneyRequest payload with station_codes ["ABC"], start_time "2025-06-16T10:00:00", max_wait 10
    When I validate the JourneyRequest
    Then a validation error should be raised containing "At least two station codes are required."

  Scenario: Station code has invalid format
    Given a JourneyRequest payload with station_codes ["ABC", "12X"], start_time "2025-06-16T10:00:00", max_wait 10
    When I validate the JourneyRequest
    Then a validation error should be raised containing "Invalid station code: 12X"

  Scenario: Start time is invalid
    Given a JourneyRequest payload with station_codes ["ABC", "DEF"], start_time "not-a-date", max_wait 10
    When I validate the JourneyRequest
    Then a validation error should be raised containing "start_time must be a valid ISO 8601 datetime string."

  Scenario: Max wait is too low
    Given a JourneyRequest payload with station_codes ["ABC", "DEF"], start_time "2025-06-16T10:00:00", max_wait 0
    When I validate the JourneyRequest
    Then a validation error should be raised containing "max_wait must be between 1 and 600 minutes."

  Scenario: Max wait is too high
    Given a JourneyRequest payload with station_codes ["ABC", "DEF"], start_time "2025-06-16T10:00:00", max_wait 601
    When I validate the JourneyRequest
    Then a validation error should be raised containing "max_wait must be between 1 and 600 minutes."

  Scenario: Valid request
    Given a JourneyRequest payload with station_codes ["ABC", "DEF"], start_time "2025-06-16T10:00:00", max_wait 30
    When I validate the JourneyRequest
    Then the request should be valid
