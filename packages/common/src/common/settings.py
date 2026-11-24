"""Typed access to app settings.

Locally these come from each app's `local.settings.json`; in Azure they are the
Function App's application settings. Both end up as environment variables.
"""

import os


class MissingSettingError(KeyError):
    """Raised when a required app setting is not configured."""


def get_setting(name: str, default: str | None = None) -> str:
    """Return the app setting `name`, or `default` when it is not set.

    Raises `MissingSettingError` when the setting is missing and no default is given.
    """
    value = os.environ.get(name, default)
    if value is None:
        msg = f"App setting {name!r} is not configured"
        raise MissingSettingError(msg)
    return value
