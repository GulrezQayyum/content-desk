from typing import Any
from datetime import date
from repository import PostRepository
from tools._common import (
    InvalidInputError,
    RuleViolatedError,
    parse_iso_date,
    validate_post_id,
    check_slot_available,
    default_repo
)

def validate (
    post_id: int,
    new_date: str,
    repo: PostRepository = default_repo,
) -> None:
    validate_post_id(post_id)
    parsed_date = parse_iso_date(new_date)
    if parsed_date < date.today():
        raise RuleViolatedError(
            f"Cannot reschedule post to a past date ({new_date} < {date.today().isoformat()})."
        )
    post = repo.get_post(post_id)
    if not post:
        raise InvalidInputError(f"Post with ID {post_id} does not exist.")
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