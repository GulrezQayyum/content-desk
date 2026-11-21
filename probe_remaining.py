import time
from pathlib import Path
from agent import run_agent
from repository import PostRepository
from tools import add_post, list_posts, mark_published, set_today

set_today("2026-11-18")

PROMPTS = [
    "Move the carousel post to Monday.",
    "Reschedule the Podcast announcement to next Tuesday",
    "Schedule a LinkedIn post titled 'Throwback' for 2026-11-10.",  
    "Schedule a Substack post titled 'Collision' for 2026-11-20.",
    "Reschedule post 1 to 2026-11-25.",
    "Publish post 42.",                                        
    "Schedule a post titled 'Hot Take' on Twitter for 2026-11-22.", 
    "Schedule a post for me.",                               
    "Move all my scheduled Substack posts forward by 7 days.",
]

def fresh_db() -> PostRepository:
    Path("probe.db").unlink(missing_ok=True)
    repo = PostRepository("probe.db")
    p1 = add_post("Launch Announcement", "Substack", "2026-11-18", repo=repo)
    mark_published(p1["id"], repo=repo)                               # #1 published
    add_post("SQLite First", "Substack", "2026-11-20", repo=repo)      # #2 Substack 11-20
    add_post("RAG Carousel", "LinkedIn", "2026-11-21", repo=repo)      # #3 carousel A
    add_post("Agent Carousel", "Medium", "2026-11-22", repo=repo)      # #4 carousel B
    add_post("Tool Contracts", "Substack", "2026-11-24", repo=repo)    # #5 Substack 11-24
    return repo

for i, prompt in enumerate(PROMPTS, 1):
    repo = fresh_db()
    out = run_agent(prompt, mode="naive", repo=repo)
    print(f"\n[{i}/9] PROMPT: {prompt}")
    print(f"STATUS: {out['status']} | TURNS: {out['turns_used']}")
    print(f"ANSWER: {out['final_answer'].strip()}")
    print("DB AFTER:", [(p["id"], p["title"], p["scheduled_date"], p["status"]) for p in list_posts(repo=repo)])
    time.sleep(2)

Path("probe.db").unlink(missing_ok=True)

