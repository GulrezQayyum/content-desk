"""
Content Desk Agent — Naive Mode Baseline

NAIVE MODE DEFINITION:
- Executes exactly ONE attempt per tool call requested by the model.
- Performs ZERO automatic retries, argument repairs, or fallback recovery.
- Wraps every tool outcome (success or exception) in `envelope.py` and feeds
  the JSON envelope back to the model as-is.
- Terminates only when the model returns a final assistant message without
  tool calls or reaches `max_turns` (default: 6).
"""

import json
import logging
from typing import Any
from dotenv import load_dotenv
from groq import Groq
from envelope import error, from_exception, ok
from repository import PostRepository
from tools import TOOL_REGISTRY, TOOL_SCHEMAS, get_today
from tools._common import default_repo

logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_TURNS = 6


def build_sys_prompt() -> str:
    today = get_today()
    weekday = today.strftime("%A")
    return (
        "You are Content Desk, a content scheduling assistant. "
        f"Today's date is {today.isoformat()} ({weekday}). "
        "Use the provided tools to manage posts across Substack, LinkedIn, and Medium. "
        "Always resolve relative dates (like 'tomorrow' or 'next Friday') using today's date."
    )


def _execute_naive_tool_call(
    tool_name: str,
    raw_args: str,
    repo: PostRepository,
) -> dict[str, Any]:
    """Single-attempt execution returning a standardized envelope."""
    tool_fn = TOOL_REGISTRY.get(tool_name)
    if tool_fn is None:
        return error(
            err_type="UnknownToolError",
            message=f"Tool '{tool_name}' does not exist.",
            retryable=False,
        )

    try:
        args = json.loads(raw_args) if raw_args else {}
        if not isinstance(args, dict):
            return error(
                err_type="InvalidInputError",
                message="Tool arguments must decode to a JSON object.",
                retryable=True,
            )
    except json.JSONDecodeError as exc:
        return error(
            err_type="InvalidInputError",
            message=f"Malformed JSON arguments: {exc}",
            retryable=True,
        )

    try:
        result = tool_fn(**args, repo=repo)
        return ok(result)
    except TypeError as exc:
        logger.warning("Argument signature mismatch for %s: %s", tool_name, exc)
        return error(
            err_type="InvalidInputError",
            message=f"Invalid arguments for '{tool_name}': {exc}",
            retryable=True,
        )
    except Exception as exc:
        return from_exception(exc)


def run_agent(
    user_prompt: str,
    *,
    mode: str = "naive",
    model: str = DEFAULT_MODEL,
    max_turns: int = MAX_TURNS,
    temperature: float = 0.1,
    repo: PostRepository = default_repo,
    client: Groq | None = None,
) -> dict[str, Any]:
    """
    Run the LLM tool-calling loop and return the final response + full message trace.
    """
    if mode != "naive":
        raise ValueError(f"Mode '{mode}' is not implemented yet. Use mode='naive'.")

    groq_client = client or Groq()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": build_sys_prompt()},
        {"role": "user", "content": user_prompt},
    ]

    turns_used = 0

    for turn in range(1, max_turns + 1):
        turns_used = turn
        logger.info("Turn %d/%d -> Calling Groq (%s)", turn, max_turns, model)

        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=temperature,
        )

        assistant_msg = response.choices[0].message
        tool_calls = assistant_msg.tool_calls or []

        assistant_record: dict[str, Any] = {
            "role": "assistant",
            "content": assistant_msg.content or "",
        }
        if tool_calls:
            assistant_record["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ]
        messages.append(assistant_record)

        if not tool_calls:
            return {
                "status": "completed",
                "mode": mode,
                "turns_used": turns_used,
                "final_answer": assistant_msg.content or "",
                "messages": messages,
            }

        for tc in tool_calls:
            fn_name = tc.function.name
            fn_args = tc.function.arguments
            logger.info("Executing tool %s(%s)", fn_name, fn_args)

            envelope = _execute_naive_tool_call(fn_name, fn_args, repo=repo)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": fn_name,
                    "content": json.dumps(envelope),
                }
            )

    logger.warning("Agent hit hard turn cap (%d turns) without finishing.", max_turns)
    return {
        "status": "max_turns_exceeded",
        "mode": mode,
        "turns_used": turns_used,
        "final_answer": "",
        "messages": messages,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    out = run_agent(
        "Schedule a Substack post titled 'Why Deterministic Tools Matter' for next Friday, "
        "then show me all scheduled posts."
    )
    print("\n=== FINAL ANSWER ===")
    print(out["final_answer"])
    print(f"(Status: {out['status']}, Turns used: {out['turns_used']})")