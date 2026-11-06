content_desk/
├── agent.py          # LLM loop, mode switch (naive / reliable)
├── reliability.py    # validate → execute → classify → retry
├── envelope.py       # result/error shapes
├── tools/            # one file per tool: schema + validator + executor
├── repository.py     # all SQLite access
├── faults.py         # fault injection
├── evals/
│   ├── cases.json
│   ├── runner.py
│   └── report.py
└── traces/           # per-run logs


## Architecture

User message
    │
    ▼
┌──────────────────────────────┐
│ Agent loop (LLM on Groq)     │  system prompt includes today's date
│ decides: answer or call tool │
└──────────────┬───────────────┘
               │ tool call (name + raw args)
               ▼
┌──────────────────────────────┐
│ Reliability layer            │  ← the part you're here to learn
│  1. Schema check (Pydantic)  │
│  2. Semantic check           │
│  3. Execute                  │
│  4. Classify any error       │
│  5. Retry / feed back / fail │
└──────────────┬───────────────┘
               │ result envelope
               ▼
┌──────────────────────────────┐
│ Tool executors → Repository  │──► SQLite (posts table)
└──────────────────────────────┘
               │
               ▼
     Envelope returns to the LLM, which replies to the user