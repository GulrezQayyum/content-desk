from typing import Any
from repository import PostRepository
from tools._common import (
    NotFoundError,
    RuleViolatedError,
    default_repo,
    validate_post_id,
)

SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "mark_published",
        "description": "Mark an existing post as published.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "Numeric ID of the post to publish."},
            },
            "required": ["post_id"],
        },
    },
}


def validate (
    post_id: int,
    repo: PostRepository = default_repo,
) -> None:
    validate_post_id(post_id)
    post = repo.get_post(post_id)
    if not post:
        raise NotFoundError(f"Post with ID {post_id} does not exist.")
    if post["status"] == "published":
        raise RuleViolatedError(f"Post with ID {post_id} is already published.")

def execute (
    post_id: int,
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    updated = repo.update_status(post_id, "published")
    assert updated is not None
    return updated

def mark_published (
    post_id: int,
    repo: PostRepository = default_repo,
) -> dict[str, Any]:
    validate(post_id=post_id, repo=repo)
    return execute(post_id=post_id, repo=repo)