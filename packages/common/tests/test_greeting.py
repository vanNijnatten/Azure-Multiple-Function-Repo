import pytest

from common import build_greeting


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Ada", "Hello, Ada!"),
        ("  Grace  ", "Hello, Grace!"),
        ("", "Hello, world!"),
        (None, "Hello, world!"),
    ],
)
def test_build_greeting(name: str | None, expected: str) -> None:
    assert build_greeting(name) == expected
