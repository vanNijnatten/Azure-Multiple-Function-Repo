import importlib.util
from pathlib import Path

import azure.functions as func
import pytest

APP_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def function_app() -> func.FunctionApp:
    """Load this app's `function_app.py` under a unique module name.

    Every Function App has a `function_app.py`, so it cannot simply be imported by
    name when the tests of several apps run in one pytest session.
    """
    spec = importlib.util.spec_from_file_location(f"{APP_DIR.name}.function_app", APP_DIR / "function_app.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.app
    assert isinstance(app, func.FunctionApp)
    return app
