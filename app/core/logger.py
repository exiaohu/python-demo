import logging
import sys
from typing import Any, MutableMapping

import structlog

from app.core.config import settings
from app.middleware.request_id import get_request_id


def add_request_id(logger: Any, log_method: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logger() -> Any:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )

    processors = [
        structlog.contextvars.merge_contextvars,  # Merge context vars (user_id, etc)
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_request_id,  # Add request_id to logs
    ]

    if settings.DEBUG:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,  # type: ignore
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


logger = setup_logger()
