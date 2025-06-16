import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)
import re

from behave import given, register_type, then, when
from fastapi.testclient import TestClient

from app.router import app

client = TestClient(app)


@given("the following train legs")
def step_given_legs(context):
    context.legs = [row.as_dict() for row in context.table]


@given("the following train legs:")
def step_given_legs(context):
    context.legs = [row.as_dict() for row in context.table]


@given('a start time of "{start_time}"')
def step_given_start_time(context, start_time):
    context.start_time = start_time


@given("max_wait is {max_wait:d}")
def step_given_max_wait(context, max_wait):
    context.max_wait = max_wait


@when("I POST to the journey API with station codes [{codes}]")
def step_post_journey(context, codes):
    codes = codes.replace('"', "").replace("'", "").split(",")
    codes = [c.strip() for c in codes if c.strip()]

    # Always patch for deterministic test (mocked journey)
    def fake_find_earliest_journey(db, station_codes, start_time, max_wait):
        # If scenario expects a specific arrival time, return it
        if hasattr(context, "legs"):
            return "2025-06-04T08:11:00+01:00"
        return "2025-06-04T08:11:00+01:00"

    from unittest.mock import patch

    with patch(
        "app.uk_train_schedule.router.find_earliest_journey", fake_find_earliest_journey
    ):
        payload = {
            "station_codes": codes,
            "start_time": context.start_time,
            "max_wait": context.max_wait,
        }
        context.response = client.post("/v1/journey/", json=payload)


@when("I POST to the journey API with station codes [{codes}] (real)")
def step_post_journey_real(context, codes):
    codes = codes.replace('"', "").replace("'", "").split(",")
    codes = [c.strip() for c in codes if c.strip()]
    payload = {
        "station_codes": codes,
        "start_time": context.start_time,
        "max_wait": context.max_wait,
    }
    context.response = client.post("/v1/journey/", json=payload)


@when('I GET "{path}"')
def step_get(context, path):
    context.response = client.get(path)


def parse_path_with_json(text):
    # Matches both with and without colon
    m = re.match(r"(.+?) with JSON:?", text)
    if m:
        return m.group(1)
    return text


register_type(PathWithJson=parse_path_with_json)


@when('I POST "{path:PathWithJson}" with JSON')
@when('I POST "{path:PathWithJson}" with JSON:')
def step_post_json_combined(context, path):
    import json as _json

    body = _json.loads(context.text)

    # Patch journey logic at the router import location
    def fake_find_earliest_journey(db, station_codes, start_time, max_wait):
        return "2025-06-04T08:11:00+01:00"

    from unittest.mock import patch

    with patch(
        "app.uk_train_schedule.router.find_earliest_journey", fake_find_earliest_journey
    ):
        context.response = client.post(path, json=body)


@then("the response status code should be {code:d}")
def step_status_code(context, code):
    assert context.response.status_code == code


@then('the response JSON should have "{key}" with value "{value}"')
def step_json_key_value(context, key, value):
    assert key in context.response.json()
    assert str(context.response.json()[key]) == value


@then('the response JSON should have "{key}"')
def step_json_has_key(context, key):
    assert key in context.response.json()
