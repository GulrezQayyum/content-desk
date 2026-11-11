from datetime import date
from repository import ALLOWED_PLATFORMS, ALLOWED_STATUSES, PostRepository


class ToolError(Exception):
    """Base exception for deterministic tool failures."""


class InvalidInputError(ToolError):
    """Bad types, malformed ISO dates, empty strings, or invalid enum values."""


class RuleViolatedError(ToolError):
    """Well-formed request that violates business rules (past date, double-booked, already published)."""


class NotFoundError(ToolError):
    """Referenced post ID does not exist."""


default_repo = PostRepository()

_override_today: date | None = None

def set_today(target_date: str | date | None) -> None:
    """
    Override today's date for deterministic eval runs or agent contexts.
    Pass None to reset back to the real system clock.
    """
    global _override_today
    if isinstance(target_date, str):
        _override_today = date.fromisoformat(target_date)
    else:
        _override_today = target_date

def get_today() -> date:
    """Return the current injected date, or fall back to system clock."""
    return _override_today if _override_today is not None else date.today()


def parse_iso_date(value: str) -> date:
    if not isinstance(value, str):
        raise InvalidInputError(f"Expected ISO date string (YYYY-MM-DD), got {type(value).__name__}.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidInputError(f"Invalid date '{value}'. Must be YYYY-MM-DD.") from exc


def validate_platform(platform: str) -> None:
    if platform not in ALLOWED_PLATFORMS:
        raise InvalidInputError(
            f"Unsupported platform '{platform}'. Allowed: {', '.join(ALLOWED_PLATFORMS)}."
        )


def validate_status(status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise InvalidInputError(
            f"Unsupported status '{status}'. Allowed: {', '.join(ALLOWED_STATUSES)}."
        )


def validate_post_id(post_id: int) -> None:
    if not isinstance(post_id, int) or isinstance(post_id, bool):
        raise InvalidInputError(f"post_id must be an integer, got {type(post_id).__name__}.")


def check_slot_available(
    repo: PostRepository,
    platform: str,
    scheduled_date: str,
    exclude_post_id: int | None = None,
) -> None:
    matches = repo.fetch_posts(platform=platform, scheduled_date=scheduled_date)
    conflicts = [p for p in matches if p["id"] != exclude_post_id]
    if conflicts:
        c = conflicts[0]
        raise RuleViolatedError(
            f"{platform} is already booked on {scheduled_date} by post #{c['id']} ('{c['title']}')."
        )