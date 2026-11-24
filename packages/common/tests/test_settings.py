import pytest

from common import get_setting
from common.settings import MissingSettingError


def test_get_setting_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_SETTING", "value")
    assert get_setting("MY_SETTING") == "value"


def test_get_setting_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MY_SETTING", raising=False)
    assert get_setting("MY_SETTING", "fallback") == "fallback"


def test_get_setting_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MY_SETTING", raising=False)
    with pytest.raises(MissingSettingError, match="MY_SETTING"):
        get_setting("MY_SETTING")
