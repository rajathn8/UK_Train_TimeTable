from behave import given, when, then
from app.uk_train_schedule.schema import JourneyRequest
from pydantic import ValidationError

@given('a JourneyRequest payload with station_codes {codes}, start_time "{start_time}", max_wait {max_wait}')
def step_given_payload(context, codes, start_time, max_wait):
    # Parse codes as a list
    codes = codes.strip('[]').replace('"', '').replace("'", '').split(',')
    codes = [c.strip() for c in codes if c.strip()]
    context.payload = {
        "station_codes": codes,
        "start_time": start_time,
        "max_wait": int(max_wait)
    }

@when('I validate the JourneyRequest')
def step_when_validate(context):
    try:
        context.result = JourneyRequest(**context.payload)
        context.error = None
    except ValidationError as exc:
        context.result = None
        context.error = str(exc)

@then('a validation error should be raised containing "{msg}"')
def step_then_error(context, msg):
    assert context.error is not None, "Expected a validation error but none was raised."
    assert msg in context.error, f"Expected error message to contain '{msg}', got: {context.error}"

@then('the request should be valid')
def step_then_valid(context):
    assert context.result is not None, "Expected a valid JourneyRequest but got validation error."
    assert context.error is None, f"Expected no error, but got: {context.error}"
