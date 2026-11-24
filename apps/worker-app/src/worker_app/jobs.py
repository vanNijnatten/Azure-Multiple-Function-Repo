"""Timer- and queue-triggered background jobs."""

import json
import logging

import azure.functions as func

from common import build_greeting

logger = logging.getLogger(__name__)

bp = func.Blueprint()

GREETINGS_QUEUE = "greetings"


@bp.function_name("heartbeat")
@bp.timer_trigger(arg_name="timer", schedule="0 */5 * * * *", run_on_startup=False)
def heartbeat(timer: func.TimerRequest) -> None:
    """Run every five minutes."""
    if timer.past_due:
        logger.warning("Heartbeat timer is past due")
    logger.info("Heartbeat")


@bp.function_name("process_greeting")
@bp.queue_trigger(  # pyright: ignore[reportUnknownMemberType] - untyped **kwargs in azure-functions
    arg_name="msg",
    queue_name=GREETINGS_QUEUE,
    connection="AzureWebJobsStorage",
)
def process_greeting(msg: func.QueueMessage) -> None:
    """Handle a message such as `{"name": "Ada"}` from the greetings queue."""
    logger.info(parse_greeting(msg.get_body().decode("utf-8")))


def parse_greeting(body: str) -> str:
    """Build the greeting for a queue message body (JSON object or plain name)."""
    try:
        payload: object = json.loads(body)
    except json.JSONDecodeError:
        return build_greeting(body)
    if isinstance(payload, dict):
        name = payload.get("name")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        return build_greeting(name if isinstance(name, str) else None)
    return build_greeting(None)
