from typing import Callable, Any
from tools._common import (
    InvalidInputError,
    NotFoundError,
    RuleViolatedError,
    ToolError,
    get_today,
    set_today,
)
from tools.add_posts import SCHEMA as ADD_POST_SCHEMA, add_post
from tools.list_posts import SCHEMA as LIST_POSTS_SCHEMA, list_posts
from tools.mark_published import SCHEMA as MARK_PUBLISHED_SCHEMA, mark_published
from tools.reschedule_post import SCHEMA as RESCHEDULE_POST_SCHEMA, reschedule_post

TOOL_SCHEMAS: list[dict[str, Any]] = [
    ADD_POST_SCHEMA,
    LIST_POSTS_SCHEMA,
    RESCHEDULE_POST_SCHEMA,
    MARK_PUBLISHED_SCHEMA,
]

TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "add_post": add_post,
    "list_posts": list_posts,
    "reschedule_post": reschedule_post,
    "mark_published": mark_published,
}

__all__ = [
    "ToolError",
    "InvalidInputError",
    "RuleViolatedError",
    "NotFoundError",
    "get_today",
    "set_today",
    "add_post",
    "list_posts",
    "reschedule_post",
    "mark_published",
    "TOOL_SCHEMAS",
    "TOOL_REGISTRY",
]