from typing import Any
from repository import PostRepository
from tools._common import (
    default_repo,
    validate_platform,
    validate_status,
    parse_iso_date
)

def validate (
    platform: str | None = None,
    status: str | None = None,
    scheduled_date: str | None = None,
) -> None:
    if platform is not None:
        validate_platform(platform)
    if status is not None:
        validate_status(status)
    if scheduled_date is not None:
        parse_iso_date(scheduled_date)

def execute(
        platform: str | None = None,
        status: str | None = None,
        scheduled_date: str | None = None,
        repo: PostRepository = default_repo,
) -> list[dict[str, Any]]:
    return repo.fetch_posts(
        platform = platform,
        status = status,
        scheduled_date = scheduled_date
)

def list_posts(
        
        platform: str | None = None,
        status: str | None = None,
        scheduled_date: str | None = None,
        repo: PostRepository = default_repo,
) -> list[dict[str, Any]]:
    validate(platform=platform, status=status, scheduled_date=scheduled_date)
    return execute(platform=platform, status=status, scheduled_date=scheduled_date, repo=repo
)