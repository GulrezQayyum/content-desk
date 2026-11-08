# Content Desk

A deterministic-first content scheduling agent built in layers: storage and validated tools first, followed by structured error envelopes, fault injection, and an LLM reliability loop.

## Current Milestone: Deterministic Core (No LLM)

- **SQLite Storage (`repository.py`)**: Plain CRUD operations over a `posts` table (`id`, `title`, `platform`, `scheduled_date`, `status`).
- **Validated Tools (`tools/`)**: Four domain tools (`add_post`, `list_posts`, `reschedule_post`, `mark_published`) separated into `validate()` and `execute()` functions.
- **Typed Exceptions (`tools/_common.py`)**: Failures raise `InvalidInputError`, `RuleViolatedError`, or `NotFoundError` (all inheriting from `ToolError`) for downstream retry/feedback routing.

## Allowed Values

- **Platforms**: `Substack`, `LinkedIn`, `Medium`
- **Statuses**: `draft`, `scheduled`, `published`
- **Dates**: ISO format (`YYYY-MM-DD`), cannot be in the past when scheduling or rescheduling.

## Project Structure

```text
content_desk/
├── repository.py         # Single source of truth constants + SQLite CRUD
├── tools/
│   ├── __init__.py       # Public exports for tools and typed exceptions
│   ├── _common.py        # Typed exceptions and shared validation helpers
│   ├── add_post.py       # Create a scheduled/draft post (no double-booking)
│   ├── list_posts.py     # Filter posts by platform, status, or date
│   ├── reschedule_post.py# Move un-published posts to a valid future date
│   └── mark_published.py # Transition a post to published
├── test_manual.py        # End-to-end verification of happy & failure paths
├── envelope.py           # [Planned] Standardized tool result/error shapes
├── reliability.py        # [Planned] Validate -> execute -> classify -> retry
├── faults.py             # [Planned] Fault injection for reliability testing
├── agent.py              # [Planned] LLM loop (naive vs. reliable modes)
└── evals/                # [Planned] Eval cases, runner, and reporting