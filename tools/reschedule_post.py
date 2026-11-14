from typing import Any
from datetime import date
from repository import PostRepository
from tools._common import (
    NotFoundError,
    RuleViolatedError,
    parse_iso_date,
    validate_post_id,
    check_slot_available,
    default_repo,
    get_today
)

SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "reschedule_post",
        "description": "Move an unpublished post to a new YYYY-MM-DD date.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "Numeric ID of the post to move."},
                "new_date": {"type": "string", "description": "New target date in YYYY-MM-DD format."},
            },
            "required": ["post_id", "new_date"],
        },
    },
}

def validate(
    post_id: int,
    new_date: str,
    repo: PostRepository = default_repo,
) -> None:
    validate_post_id(post_id)
    parsed_date = parse_iso_date(new_date)
    today = get_today()
    if parsed_date < today():
        raise RuleViolatedError(
            f"Cannot reschedule post to a past date ({new_date} < {date.today().isoformat()})."
        )
    post = repo.get_post(post_id)
    if not post:
        raise NotFoundError(f"Post with ID {post_id} does not exist.")
    if post["status"] == "published":
        raise RuleViolatedError(
            f"Post with ID {post_id} is already published and cannot be rescheduled."
        )
    check_slot_available(repo, platform=post["platform"], scheduled_date=new_date, exclude_post_id=post_id)

def execute (
    post_id: int,
    new_date: str,
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    updated = repo.update_date(post_id, new_date)
    assert updated is not None
    return updated

def reschedule_post (
    post_id: int,
    new_date: str,
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    validate(post_id=post_id, new_date=new_date, repo=repo)
    return execute(post_id=post_id, new_date=new_date, repo=repo
)