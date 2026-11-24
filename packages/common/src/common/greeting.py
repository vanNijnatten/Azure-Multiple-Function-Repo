"""A tiny piece of shared business logic, used by both Function Apps."""

DEFAULT_NAME = "world"


def build_greeting(name: str | None = None) -> str:
    """Return a friendly greeting.

    >>> build_greeting("Ada")
    'Hello, Ada!'
    >>> build_greeting()
    'Hello, world!'
    """
    cleaned = (name or "").strip()
    return f"Hello, {cleaned or DEFAULT_NAME}!"
