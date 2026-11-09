from datetime import date, timedelta
from pathlib import Path
from repository import PostRepository
from tools import (
    InvalidInputError,
    NotFoundError,
    RuleViolatedError,
    ToolError,
    add_post,
    list_posts,
    mark_published,
    reschedule_post,
)

TEST_DB = Path("test_manual.db")


def check(label: str, fn, expect_err: type[ToolError] | None = None) -> None:
    try:
        res = fn()
        if expect_err:
            print(f"[FAIL] {label}: expected {expect_err.__name__}, got {res}")
        else:
            print(f"[PASS] {label} -> {res}")
    except ToolError as exc:
        if expect_err and isinstance(exc, expect_err):
            print(f"[PASS] {label} -> {type(exc).__name__}: {exc}")
        else:
            print(f"[FAIL] {label}: unexpected {type(exc).__name__}: {exc}")


def main() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()

    repo = PostRepository(TEST_DB)
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    next_week = (today + timedelta(days=7)).isoformat()
    yesterday = (today - timedelta(days=1)).isoformat()

    print("--- HAPPY PATHS ---")
    check("add Substack post", lambda: add_post("SQLite First", "Substack", tomorrow, repo=repo))
    check("add LinkedIn post same day", lambda: add_post("Tool Contracts", "LinkedIn", tomorrow, repo=repo))
    check("list all posts", lambda: list_posts(repo=repo))
    check("reschedule post #1", lambda: reschedule_post(1, next_week, repo=repo))
    check("mark post #2 published", lambda: mark_published(2, repo=repo))

    print("\n--- FAILURE PATHS ---")
    # add_post
    check("add_post bad platform", lambda: add_post("X", "Twitter", tomorrow, repo=repo), InvalidInputError)
    check("add_post past date", lambda: add_post("X", "Medium", yesterday, repo=repo), RuleViolatedError)
    check("add_post double-booked", lambda: add_post("X", "Substack", next_week, repo=repo), RuleViolatedError)

    # reschedule_post
    check("reschedule missing post", lambda: reschedule_post(99, next_week, repo=repo), NotFoundError)
    check("reschedule published post", lambda: reschedule_post(2, next_week, repo=repo), RuleViolatedError)
    check("reschedule to past date", lambda: reschedule_post(1, yesterday, repo=repo), RuleViolatedError)
    add_post("Substack 2", "Substack", tomorrow, repo=repo)  # id=3
    check("reschedule double-booked", lambda: reschedule_post(1, tomorrow, repo=repo), RuleViolatedError)

    # mark_published
    check("publish missing post", lambda: mark_published(99, repo=repo), NotFoundError)
    check("publish already published", lambda: mark_published(2, repo=repo), RuleViolatedError)

    # list_posts
    check("list invalid platform", lambda: list_posts(platform="Reddit", repo=repo), InvalidInputError)
    check("list invalid status", lambda: list_posts(status="deleted", repo=repo), InvalidInputError)
    check("list invalid date", lambda: list_posts(scheduled_date="2026-99-99", repo=repo), InvalidInputError)

    if TEST_DB.exists():
        TEST_DB.unlink()


if __name__ == "__main__":
    main()
