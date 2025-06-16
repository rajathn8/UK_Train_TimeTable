import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)
from behave import then, when
from pydantic import ValidationError

from app.uk_train_schedule.schema import JourneyRequest


@when("I validate the JourneyRequest")
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
    assert (
        msg in context.error
    ), f"Expected error message to contain '{msg}', got: {context.error}"


@then("the request should be valid")
def step_then_valid(context):
    assert (
        context.result is not None
    ), "Expected a valid JourneyRequest but got validation error."
    assert context.error is None, f"Expected no error, but got: {context.error}"
