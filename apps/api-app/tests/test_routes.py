import json

import azure.functions as func
import pytest

from api_app.routes import health, hello


def make_request(
    method: str = "GET",
    params: dict[str, str] | None = None,
    body: bytes = b"",
) -> func.HttpRequest:
    return func.HttpRequest(method=method, url="/api/hello", params=params or {}, body=body)


def test_health_returns_ok() -> None:
    response = health(make_request())
    assert response.status_code == 200
    assert json.loads(response.get_body()) == {"status": "ok"}


@pytest.mark.parametrize(
    ("request_", "expected"),
    [
        (make_request(params={"name": "Ada"}), "Hello, Ada!"),
        (make_request("POST", body=b'{"name": "Grace"}'), "Hello, Grace!"),
        (make_request("POST", body=b'{"name": 42}'), "Hello, world!"),
        (make_request(), "Hello, world!"),
    ],
)
def test_hello_greets(request_: func.HttpRequest, expected: str) -> None:
    response = hello(request_)
    assert response.status_code == 200
    assert json.loads(response.get_body()) == {"message": expected}


def test_hello_rejects_invalid_json() -> None:
    response = hello(make_request("POST", body=b"not json"))
    assert response.status_code == 400
