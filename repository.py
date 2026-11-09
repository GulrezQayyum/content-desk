import sqlite3
from pathlib import Path
from typing import Any, List

ALLOWED_PLATFORMS = ["LinkedIn", "Substack", "Medium"]
ALLOWED_STATUSES = ["draft", "published", "scheduled"]

DEFAULT_DB_PATH = Path("content-desk.db")


class PostRepository:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        platforms_sql = ", ".join(f"'{platform}'" for platform in ALLOWED_PLATFORMS)
        statuses_sql = ", ".join(f"'{status}'" for status in ALLOWED_STATUSES)

        query = f"""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            platform TEXT NOT NULL CHECK (platform IN ({platforms_sql})),
            scheduled_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ({statuses_sql}))
        );
        """
        with self._connect() as conn:
            conn.execute(query)

    def insert_post(self, title: str, platform: str, scheduled_date: str, status: str) -> dict[str, Any]:
        query = """
        INSERT INTO POSTS (title, platform, scheduled_date, status)
        VALUES(?, ?, ?, ?)
        """
        with self._connect() as conn:
            cursor = conn.execute(query, (title, platform, scheduled_date, status))
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def get_post(self, post_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (post_id,)
            ).fetchone()
            return dict(row) if row else None

    def fetch_posts(
            self,
            platform: str | None = None,
            status: str | None = None,
            scheduled_date: str | None = None,
            ) -> list[dict[str, Any]]:
            clauses: List[str] = []
            params: List[Any] = []

            if platform is not None:
                clauses.append("platform = ?")
                params.append(platform)
            if status is not None:
                clauses.append("status = ?")
                params.append(status)
            if scheduled_date is not None:
               clauses.append("scheduled_date = ?")
               params.append(scheduled_date)

            where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            query = f"SELECT * FROM posts {where_sql} ORDER BY scheduled_date ASC, id ASC"

            with self._connect() as conn:
               rows = conn.execute(query, params).fetchall()
               return [dict(row) for row in rows]

    def update_date(self, post_id: int, new_date: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE posts SET scheduled_date = ? WHERE id = ?", (new_date, post_id)
                )
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (post_id,)
            ).fetchone()
            return dict(row) if row else None

    def update_status(self, post_id: int, new_status: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE posts SET status = ? WHERE id = ?", (new_status, post_id)
            )
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (post_id,)
            ).fetchone()
            return dict(row) if row else None




                    