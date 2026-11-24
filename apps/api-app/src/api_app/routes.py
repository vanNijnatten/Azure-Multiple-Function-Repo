"""HTTP-triggered functions.

Functions live on a `Blueprint` inside the package (not in `function_app.py`), so
they are importable, type checked and testable like any other code.
"""

import json
import logging

import azure.functions as func

from common import build_greeting

logger = logging.getLogger(__name__)

bp = func.Blueprint()


@bp.function_name("health")
@bp.route(route="health", methods=[func.HttpMethod.GET], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Liveness probe that does not need a function key."""
    return func.HttpResponse(
        json.dumps({"status": "ok"}),
        mimetype="application/json",
    )


@bp.function_name("hello")
@bp.route(route="hello", methods=[func.HttpMethod.GET, func.HttpMethod.POST])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    """Greet the caller by the `name` query parameter or JSON body field."""
    name = req.params.get("name")
    if name is None and req.get_body():
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse("Request body must be valid JSON", status_code=400)
        if isinstance(body, dict):
            raw_name = body.get("name")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            name = raw_name if isinstance(raw_name, str) else None

    logger.info("Greeting requested for %r", name)
    return func.HttpResponse(
        json.dumps({"message": build_greeting(name)}),
        mimetype="application/json",
    )
