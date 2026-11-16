# content-desk

A deterministic-first content scheduling agent built in Python, SQLite, and Groq.

## Architecture

1. **Storage (`repository.py`)**
   - Single source of truth for allowed platforms (`LinkedIn`, `Substack`, `Medium`) and statuses (`draft`, `scheduled`, `published`).
   - Enforces database-level `CHECK` constraints in SQLite.

2. **Deterministic Tools (`tools/`)**
   - Each tool (`add_post`, `list_posts`, `reschedule_post`, `mark_published`) owns its JSON `SCHEMA` and separates pre-flight checks (`validate()`) from database writes (`execute()`).
   - Raises typed domain exceptions (`InvalidInputError`, `NotFoundError`, `RuleViolatedError`).
   - Uses an injectable `get_today()` / `set_today()` clock so relative date prompts stay deterministic during testing.

3. **Standardized Envelopes (`envelope.py`)**
   - Wraps every tool outcome into one JSON shape (`status`, `result`, `error`) so the LLM never receives raw Python exceptions.
   - Maps `InvalidInputError` to `retryable: true` and domain rejections (`RuleViolatedError`, `NotFoundError`) to `retryable: false`, while logging unexpected crashes cleanly.

4. **Agent Loop (`agent.py` — Naive Mode Baseline)**
   - Injects today's ISO date and weekday into the system prompt and enforces a hard cap of `6` turns at low temperature (`0.1`).
   - Executes one attempt per tool call with zero automatic retries, establishing a clean baseline before adding `reliability.py`.

## Project Structure

```text
content-desk/
├── agent.py            # Groq tool-calling loop (Naive Mode baseline)
├── envelope.py         # Standardized result/error wrapper & logging
├── repository.py       # SQLite persistence & enum constraints
├── test_manual.py      # 16 deterministic happy/failure path checks
├── tools/
│   ├── _common.py      # Typed exceptions, validators & injectable clock
│   ├── add_posts.py
│   ├── list_posts.py
│   ├── mark_published.py
│   └── reschedule_post.py
└── traces/             # Execution trace storage

## Quickstart

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Groq API key
echo 'GROQ_API_KEY="your-api-key"' > .env

# 3. Run deterministic tool regression checks
python3 test_manual.py

# 4. Run the agent in Naive Mode
python3 agent.py