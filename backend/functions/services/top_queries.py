from fastapi import APIRouter
import sqlite3
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"


def conn():
    return sqlite3.connect(DB_PATH)

@router.get("/top-subjects")
def top_subjects(limit: int = 10):
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT 
                e.qid,
                COALESCE(e.label, e.qid),
                COUNT(DISTINCT qr.query_id) AS occurrences
            FROM query_results qr
            LEFT JOIN entities e ON e.qid = qr.subject_qid
            GROUP BY qr.subject_qid
            ORDER BY occurrences DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
    return [
        {"qid": r[0], "label": r[1], "occurrences": r[2]}
        for r in rows
    ]

@router.get("/top-predicates")
def top_predicates(limit: int = 10):
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT 
                p.pid,
                COALESCE(p.label, p.pid),
                COUNT(DISTINCT qr.query_id) AS occurrences
            FROM query_results qr
            LEFT JOIN predicates p ON p.pid = qr.predicate_pid
            GROUP BY qr.predicate_pid
            ORDER BY occurrences DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
    return [
        {"pid": r[0], "label": r[1], "occurrences": r[2]}
        for r in rows
    ]

@router.get("/top-triplets")
def top_triplets(limit: int = 10):
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT 
                qr.triple,
                AVG(qr.score) as avg_score,
                COUNT(*) as occurrences
            FROM query_results qr
            GROUP BY qr.triple
            ORDER BY avg_score DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()

    return [
        {
            "triple": r[0],
            "avg_score": round(r[1], 4),
            "occurrences": r[2]
        }
        for r in rows
    ]
