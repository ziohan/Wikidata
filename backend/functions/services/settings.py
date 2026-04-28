from fastapi import APIRouter
import sqlite3
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"

def conn():
    return sqlite3.connect(DB_PATH)


@router.get("/settings")
def get_settings():
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall()
        settings = {k: v for k, v in rows}

        return {
            "default_hops": int(settings.get("default_hops", 1)),
            "default_top_n": int(settings.get("default_top_n", 10))
        }

@router.post("/settings")
def update_settings(data: dict):
    with conn() as c:
        cur = c.cursor()
        for key, value in data.items():
            cur.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))
        c.commit()

    return {"status": "ok"}

@router.delete("/clear-queries")
def clear_queries():
    with conn() as c:
        cur = c.cursor()
        cur.execute("DELETE FROM query_results")
        cur.execute("DELETE FROM queries")
        c.commit()

    return {"status": "all queries deleted"}