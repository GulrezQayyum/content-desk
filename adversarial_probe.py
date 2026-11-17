"""
Adversarial Probe — Hand-crafted stress test for Naive Mode.

Seeds an isolated SQLite database with tricky state (published posts,
ambiguous titles, occupied slots) and runs 14 adversarial prompts across
6 failure categories, saving full traces to `traces/adversarial_naive.json`.
"""

import json
import logging
from pathlib import Path
from agent import DEFAULT_MODEL, run_agent
from repository import PostRepository
from tools import add_post, mark_published, set_today

# Fixed clock: Wednesday, 2026-11-18
# - "tomorrow"    -> 2026-11-19 (Thursday)
# - "this Friday" -> 2026-11-20
# - "next Friday" -> 2026-11-27 (or 2026-11-20 depending on model interpretation)
# - "end of month"-> 2026-11-30 (Monday)
FIXED_TODAY = "2026-11-18"

ADVERSARIAL_CASES = [
    # 1. Ambiguous dates
    {"id": "date_tomorrow", "category": "Ambiguous dates", "prompt": "Schedule a Medium post titled 'Daily Notes' for tomorrow."},
    {"id": "date_this_friday", "category": "Ambiguous dates", "prompt": "Schedule a LinkedIn post titled 'Friday Wrap' for this Friday."},
    {"id": "date_next_friday", "category": "Ambiguous dates", "prompt": "Schedule a Substack post titled 'Deep Dive' for next Friday."},
    {"id": "date_eom", "category": "Ambiguous dates", "prompt": "Draft a Medium post titled 'November Recap' for the end of the month."},

    # 2. Ambiguous references (DB has two 'Carousel' posts and zero 'Podcast' posts)
    {"id": "ref_ambiguous", "category": "Ambiguous references", "prompt": "Move the carousel post to Monday."},
    {"id": "ref_zero_match", "category": "Ambiguous references", "prompt": "Reschedule the podcast announcement to next Tuesday."},

    # 3. Rule violations (DB already has Substack booked on 2026-11-20 and post #1 published)
    {"id": "rule_past_date", "category": "Rule violations", "prompt": "Schedule a LinkedIn post titled 'Throwback' for 2026-11-10."},
    {"id": "rule_double_book", "category": "Rule violations", "prompt": "Schedule a Substack post titled 'Collision Test' for 2026-11-20."},
    {"id": "rule_edit_published", "category": "Rule violations", "prompt": "Reschedule post 1 to 2026-11-25."},

    # 4. Nonexistent things
    {"id": "nonexist_id", "category": "Nonexistent things", "prompt": "Publish post 42."},
    {"id": "nonexist_platform", "category": "Nonexistent things", "prompt": "Schedule a post titled 'Hot Take' on Twitter for 2026-11-22."},

    # 5. Missing info (Does it ask, or hallucinate/invent values?)
    {"id": "missing_all", "category": "Missing info", "prompt": "Schedule a post for me."},
    {"id": "missing_date", "category": "Missing info", "prompt": "Schedule a LinkedIn post titled 'Untitled Thoughts'."},

    # 6. Multi-step requests
    {"id": "multistep_shift_all", "category": "Multi-step requests", "prompt": "Move all my scheduled Substack posts forward by 7 days."},
]


def seed_repo(db_path: Path) -> PostRepository:
    """Create a fresh SQLite DB with controlled edge-case state."""
    if db_path.exists():
        db_path.unlink()

    repo = PostRepository(db_path=str(db_path))

    # Post #1: Already published (cannot be rescheduled)
    p1 = add_post("Launch Announcement", "Substack", "2026-11-18", repo=repo)
    mark_published(p1["id"], repo=repo)

    # Post #2: Scheduled Substack on 2026-11-20 (blocks double-booking on 11-20)
    add_post("SQLite First", "Substack", "2026-11-20", repo=repo)

    # Post #3 & #4: Two ambiguous "Carousel" posts
    add_post("RAG Architecture Carousel", "LinkedIn", "2026-11-21", repo=repo)
    add_post("Agent Reliability Carousel", "Medium", "2026-11-22", repo=repo)

    # Post #5: Second scheduled Substack post for the multi-step shift test
    add_post("Tool Contracts", "Substack", "2026-11-24", repo=repo)

    return repo


def extract_tool_trace(messages: list[dict]) -> list[dict]:
    """Pair each assistant tool call with its corresponding tool envelope."""
    trace = []
    envelopes_by_id = {
        m["tool_call_id"]: json.loads(m["content"])
        for m in messages
        if m.get("role") == "tool"
    }
    for m in messages:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                tc_id = tc["id"]
                trace.append(
                    {
                        "tool": tc["function"]["name"],
                        "args": tc["function"]["arguments"],
                        "envelope": envelopes_by_id.get(tc_id),
                    }
                )
    return trace


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")
    set_today(FIXED_TODAY)

    db_path = Path("adversarial_test.db")
    trace_path = Path("traces/adversarial_naive.json")
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    results = []

    print(f"Running {len(ADVERSARIAL_CASES)} adversarial prompts (Today = {FIXED_TODAY}, Model = {DEFAULT_MODEL})\n")
    print("=" * 80)

    for case in ADVERSARIAL_CASES:
        # Reset DB before every case so prompts don't pollute each other
        repo = seed_repo(db_path)

        out = run_agent(case["prompt"], mode="naive", repo=repo)
        tool_trace = extract_tool_trace(out["messages"])

        record = {
            "id": case["id"],
            "category": case["category"],
            "prompt": case["prompt"],
            "status": out["status"],
            "turns_used": out["turns_used"],
            "tool_calls": tool_trace,
            "final_answer": out["final_answer"],
        }
        results.append(record)

        print(f"[{case['category']}] ({case['id']})")
        print(f"  Prompt : {case['prompt']}")
        if not tool_trace:
            print("  Tools  : (none — answered directly)")
        for step in tool_trace:
            env = step["envelope"] or {}
            err_info = f" -> {env['error']['type']}: {env['error']['message']}" if env.get("status") == "error" else " -> ok"
            print(f"  Tool   : {step['tool']}({step['args']}){err_info}")
        print(f"  Answer : {out['final_answer'].strip()}")
        print("-" * 80)

    trace_path.write_text(json.dumps(results, indent=2))
    if db_path.exists():
        db_path.unlink()

    print(f"\nFull trace saved to {trace_path}")


if __name__ == "__main__":
    main()