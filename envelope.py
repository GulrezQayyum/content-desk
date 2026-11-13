from typing import Any
import logging
from tools._common import (
    InvalidInputError,
    RuleViolatedError,
    NotFoundError,
    ToolError
)

logger = logging.getLogger(__name__)


def ok(result: Any) -> dict[str, Any]:
    """Wrap a successful tool return value into the standard envelope."""
    return {
        "status": "ok",
        "result": result,
        "error": None
    }

def error(err_type: str, message: str, retryable: bool) -> dict[str, Any]:
    """Build a standardized error envelope."""
    return {
        "status": "error",
        "result": None,
        "error": {
            "type": err_type,
            "message": message,
            "retryable": retryable
        },
    }

def from_exception(exc: Exception) -> dict[str, Any]:
    """
    Map a raised exception into the standard error envelope.
    - InvalidInputError -> retryable=True (model can fix arguments)
    - RuleViolatedError / NotFoundError -> retryable=False (domain block)
    - Unexpected Exception -> logged with full traceback, mapped to InternalError (retryable=False)
    """
    if isinstance(exc, InvalidInputError):
        logger.warning("Tool input error: %s", exc)
        return error(
            err_type= "InvalidInputError",
            message= str(exc),
            retryable= True
        )
    if isinstance(exc, (RuleViolatedError, NotFoundError)):
        logger.info("Tool domain error (%s): %s", type(exc).__name__, exc)
        return error(
            err_type= type(exc).__name__,
            message= str(exc),
            retryable= False
        )
    if isinstance(exc, ToolError):
        logger.warning("Unhandled ToolError (%s): %s", type(exc).__name__, exc)
        return error(
            err_type=type(exc).__name__,
            message=str(exc),
            retryable=False,
        )
    logger.exception("Unexpected internal error in tool execution")
    return error(
        err_type= "InternalError",
        message= "An unexpected internal error occurred while running the tool.",
        retryable= False
    )
    