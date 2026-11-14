from typing import Any
from repository import ALLOWED_PLATFORMS, ALLOWED_STATUSES, PostRepository
from tools._common import (
    InvalidInputError,
    RuleViolatedError,
    check_slot_available,
    default_repo,
    get_today,
    parse_iso_date,
    validate_platform,
    validate_status,
)

SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "add_post",
        "description": "Schedule or draft a new post. Only one post per platform per day is allowed.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Headline or working title of the post."},
                "platform": {"type": "string", "enum": list(ALLOWED_PLATFORMS)},
                "scheduled_date": {"type": "string", "description": "Target date in YYYY-MM-DD format."},
                "status": {
                    "type": "string",
                    "enum": list(ALLOWED_STATUSES),
                    "default": "scheduled",
                },
            },
            "required": ["title", "platform", "scheduled_date"],
        },
    },
}

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
    today = get_today()
    if parsed_date < today:
        raise RuleViolatedError(
            f"Cannot schedule post in the past ({scheduled_date} < {today.isoformat()})."
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
        title=title,
        platform=platform,
        scheduled_date=scheduled_date,
        status=status,
    )


def add_post(
    title: str,
    platform: str,
    scheduled_date: str,
    status: str = "scheduled",
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    validate(title, platform, scheduled_date, status, repo=repo)
    return execute(title, platform, scheduled_date, status, repo=repo)