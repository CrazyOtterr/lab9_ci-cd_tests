import pytest
import requests


BASE_URL = "https://httpbingo.org"
DEFAULT_TIMEOUT = 15


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def session():
    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/json"})
        original_request = s.request

        def request_with_timeout(method, url, **kwargs):
            kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
            return original_request(method, url, **kwargs)

        s.request = request_with_timeout
        yield s