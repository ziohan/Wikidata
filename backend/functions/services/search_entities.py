from fastapi import APIRouter
import sqlite3
from pathlib import Path
import math

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"


@router.get("/search-entities")
def search_entities(page: int = 1, page_size: int = 10, search: str = "", favorite: bool = False, sort_by: str = "occurrences", order: str = "desc"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    offset = (page - 1) * page_size

    occurrences_subquery = """
        SELECT
            e.qid AS qid,
            COUNT(DISTINCT qr.query_id) AS occurrences
        FROM entities e
        LEFT JOIN query_results qr ON qr.triple LIKE e.qid || '%' OR qr.triple LIKE '% ' || e.qid || ' %' OR qr.triple LIKE '% ' || e.qid
        GROUP BY e.qid
    """

    base_sql = f"""
        FROM entities e
        LEFT JOIN ({occurrences_subquery}) o ON o.qid = e.qid
        LEFT JOIN entity_favorites ef ON ef.qid = e.qid
        WHERE 1=1
    """

    params = []
    if search:
        base_sql += " AND (e.qid LIKE ? OR e.label LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if favorite:
        base_sql += " AND ef.qid IS NOT NULL"

    sort_map = {
        "qid": "e.qid",
        "label": "e.label",
        "occurrences": "COALESCE(o.occurrences, 0)"
    }
    order_sql = f"""
        ORDER BY {sort_map.get(sort_by, 'COALESCE(o.occurrences,0)')} {order.upper()}
    """
    cursor.execute(f"""
        SELECT COUNT(*)
        {base_sql}
    """, params)
    total = cursor.fetchone()[0]

    sql = f"""
        SELECT
            e.qid,
            COALESCE(e.label, e.qid, 'Unknown'),
            COALESCE(o.occurrences, 0),
            CASE WHEN ef.qid IS NOT NULL THEN 1 ELSE 0 END as favorite
        {base_sql}
        {order_sql}
        LIMIT ? OFFSET ?
    """

    cursor.execute(sql, params + [page_size, offset])
    rows = cursor.fetchall()
    conn.close()
    return {
        "data": [
            {
                "qid": r[0],
                "label": r[1],
                "occurrences": r[2],
                "favorite": bool(r[3])
            }
            for r in rows
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, math.ceil(total / page_size))
        }
    }

@router.patch("/entities/{qid}/favorite")
def toggle_entity_favorite(qid: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_favorites (
            qid TEXT PRIMARY KEY
        )
    """)

    cursor.execute("SELECT qid FROM entity_favorites WHERE qid = ?", (qid,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM entity_favorites WHERE qid = ?", (qid,))
        state = False
    else:
        cursor.execute("INSERT INTO entity_favorites (qid) VALUES (?)", (qid,))
        state = True

    conn.commit()
    conn.close()
    return {
        "qid": qid,
        "favorite": state
    }