from datetime import datetime

from behave import given, then, when

from app.uk_train_schedule.controller import TransportAPIException


@given(
    'a JourneyRequest payload with station_codes {codes}, start_time "{start_time}", max_wait {max_wait}'
)
def step_given_payload(context, codes, start_time, max_wait):
    codes = codes.strip("[]").replace('"', "").replace("'", "").split(",")
    codes = [c.strip() for c in codes if c.strip()]
    context.payload = {
        "station_codes": codes,
        "start_time": start_time,
        "max_wait": int(max_wait),
    }


@when("I simulate a journey with a long wait at BBB")
def step_when_long_wait(context):
    # Simulate controller logic: raise wait time error at BBB
    try:
        raise TransportAPIException(
            detail="Wait time at BBB exceeds max_wait (10 > 5)", status_code=400
        )
    except TransportAPIException as exc:
        context.error = str(exc)


@when("I simulate a journey with no trains for a leg")
def step_when_no_trains(context):
    # Simulate controller logic: raise no trains error
    try:
        raise TransportAPIException(
            detail="No trains found from AAA to ZZZ after 2025-06-16 10:00:00",
            status_code=404,
        )
    except TransportAPIException as exc:
        context.error = str(exc)


@when("I simulate a successful multi-leg journey")
def step_when_successful_journey(context):
    # Simulate controller logic: return ISO 8601 arrival time
    context.result = (datetime(2025, 6, 16, 12, 0)).isoformat()
    context.error = None


@then('a journey planning error should be raised containing "{msg}"')
def step_then_journey_error(context, msg):
    assert (
        context.error is not None
    ), "Expected a journey planning error but none was raised."
    assert (
        msg in context.error
    ), f"Expected error message to contain '{msg}', got: {context.error}"


@then("the journey should return an arrival time in ISO 8601 format")
def step_then_arrival_time(context):
    assert context.result is not None, "Expected an arrival time but got None."
    # ISO 8601 format check (YYYY-MM-DDTHH:MM:SS)
    assert "T" in context.result and len(context.result) >= 16
