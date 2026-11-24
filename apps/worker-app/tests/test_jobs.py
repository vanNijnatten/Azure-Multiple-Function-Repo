import logging

import azure.functions as func
import pytest
from pytest_mock import MockerFixture

from worker_app.jobs import heartbeat, parse_greeting, process_greeting


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('{"name": "Ada"}', "Hello, Ada!"),
        ('{"name": 42}', "Hello, world!"),
        ("[1, 2]", "Hello, world!"),
        ("Grace", "Hello, Grace!"),
    ],
)
def test_parse_greeting(body: str, expected: str) -> None:
    assert parse_greeting(body) == expected


def test_process_greeting_logs_greeting(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        process_greeting(func.QueueMessage(body=b'{"name": "Ada"}'))
    assert "Hello, Ada!" in caplog.text


def test_heartbeat_warns_when_past_due(mocker: MockerFixture, caplog: pytest.LogCaptureFixture) -> None:
    timer = mocker.create_autospec(func.TimerRequest, instance=True, past_due=True)
    with caplog.at_level(logging.INFO):
        heartbeat(timer)
    assert "past due" in caplog.text
