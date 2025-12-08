import json
import pytest

from src.api.http import HttpClient
from src.core import data_factory
from src.core.allure_utils import attach_text


@pytest.fixture(scope="session")
def http():
    """
    Provides a shared HttpClient instance for all tests.

    Using `yield` instead of `return` allows us to add proper teardown
    logic later (e.g. closing underlying HTTP session) without changing tests.
    """
    client = HttpClient()
    try:
        yield client
    finally:
        session = getattr(client, "session", None)
        if session is not None:
            session.close()


@pytest.fixture
def user_payload():
    """
    Generates a random user payload using Faker and attaches it to Allure.
    """
    payload = data_factory.generate_user_payload()
    attach_text(
        name="user_payload",
        content=json.dumps(payload.to_dict(), indent=2),
    )
    return payload


@pytest.fixture
def random_query():
    """
    Generates random query parameters and attaches them to Allure.
    """
    params = data_factory.generate_query_param()
    attach_text(
        name="random_query",
        content=json.dumps(params, indent=2),
    )
    return params
