What Worked Well in Naive Mode
Ambiguity & Missing Info ([1], [2], [8]): Refused to guess between two carousel posts, didn't hallucinate a podcast post, and asked for missing title/platform/date instead of inventing fake data.

Rule & Schema Enforcement ([3], [4], [5], [6], [7]): Handled past dates, double-bookings, published-post immutability, unknown ID #42, and unsupported platform Twitter cleanly—leaving the DB untouched and explaining why.

The Surprising Failure Modes You Discovered
Calendar Math Hallucinations (this Friday / next Friday): When today was Wednesday 2026-11-18, the model scheduled both "this Friday" and "next Friday" on 2026-11-22 (Sunday instead of Friday 11-20 / 11-27)—silently writing wrong dates to SQLite while claiming success.

Groq Strict null Schema Validation (tool_use_failed): When optional parameters were omitted, the model emitted "platform": null, crashing with HTTP 400 (BadRequestError) until ["string", "null"] was added to list_posts's schema (note: check add_post's optional status field too!).

Unbounded Retry Loop on Tool Errors: Earlier when reschedule_post threw a TypeError (InvalidInputError with retryable=True), the model looped 5 times in a row trying the broken call until hitting the 6-turn cap—showing why reliability.py needs a per-tool/per-error retry budget.

Multi-Step Ordering Collision ([9]): Moving Substack posts (11-20 and 11-24) forward by 7 days worked only because 11-27 happened to be empty. If two Substack posts had been on 11-20 and 11-27, moving 11-20 first would collide with 11-27 unless processed in reverse chronological order.

Model Size Variance: openai/gpt-oss-120b is a large frontier-class model; running the same suite against openai/gpt-oss-20b (or across 3 runs per case) will reveal higher variance in argument formatting, premature guessing, and multi-step execution