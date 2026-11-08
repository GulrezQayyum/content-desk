from datetime import date
from typing import Any
from repository import PostRepository
from tools._common import (
    InvalidInputError,
    NotFoundError,
    RuleViolatedError,
    RuleVoilatedError,
    parse_iso_date,
    validate_platform,
    validate_status,
    validate_post_id,
    check_slot_available,
    default_repo
)

# SCHEMA = {...}  # Will live here when LLM loop is added

def validate(
        title: str,
        platform: str,
        scheduled_date: str,
        status: str = "scheduled",
        repo: PostRepository = default_repo,
) -> None:
    if not isinstance(title, str) or not title.strip():
        raise InvalidInputError("Title must be a non-empty string.")

    validate_platform(platform)
    validate_status(status)

    parsed_date = parse_iso_date(scheduled_date)
    if parsed_date < date.today():
        raise RuleViolatedError(
            f"Cannot schedule post in the past ({scheduled_date} < {date.today().isoformat()})."
)

    check_slot_available(repo, platform=platform, scheduled_date=scheduled_date)


def execute(
    title: str,
    platform: str,
    scheduled_date: str,
    status: str = "scheduled",
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    return repo.insert_post(
        title = title,
        platform = platform,
        scheduled_date = scheduled_date,
        status = status
)

def add_post(
    title: str,
    platform: str,
    scheduled_date: str,
    status: str = "scheduled",
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    validate(title, platform, scheduled_date, status, repo = repo)
    return execute(title, platform, scheduled_date, status, repo = repo)