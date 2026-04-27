from fastapi import APIRouter
import sqlite3
from pathlib import Path
import math

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"


@router.get("/last-queries")
def get_last_queries(
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    favorite: bool = False,
    start_date: str = None,
    end_date: str = None
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    offset = (page - 1) * page_size
    base_sql = """
        FROM queries q
        WHERE 1=1
    """
    params = []
    if search:
        base_sql += " AND q.title LIKE ?"
        params.append(f"%{search}%")
    if favorite:
        base_sql += " AND q.favorite = 1"
    if start_date:
        base_sql += " AND date(q.created_at) >= date(?)"
        params.append(start_date)
    if end_date:
        base_sql += " AND date(q.created_at) <= date(?)"
        params.append(end_date)

    cursor.execute(f"SELECT COUNT(*) {base_sql}", params)
    total = cursor.fetchone()[0]
    total_pages = max(1, math.ceil(total / page_size))

    sql = f"""
        SELECT q.id, q.title, q.hops, q.top_n, q.created_at, q.favorite,
        (SELECT COUNT(*) FROM query_results r WHERE r.query_id = q.id) as triple_count
        {base_sql}
        ORDER BY q.created_at DESC
        LIMIT ? OFFSET ?
    """

    cursor.execute(sql, params + [page_size, offset])
    rows = cursor.fetchall()
    conn.close()

    return {
        "data": [
            {
                "id": r[0],
                "title": r[1],
                "hops": r[2],
                "top_n": r[3],
                "created_at": r[4],
                "favorite": bool(r[5]),
                "triples": r[6]
            }
                    
            for r in rows
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    }

@router.patch("/queries/{query_id}/favorite")
def toggle_favorite(query_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT favorite FROM queries WHERE id = ?
    """, (query_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"error": "Query not found"}

    new_value = 0 if row[0] == 1 else 1
    cursor.execute("""
        UPDATE queries
        SET favorite = ?
        WHERE id = ?
    """, (new_value, query_id))
    conn.commit()
    conn.close()

    return {
        "id": query_id,
        "favorite": new_value
    }

@router.delete("/queries/{query_id}")
def delete_query(query_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM query_results WHERE query_id = ?", (query_id,))
    cursor.execute("DELETE FROM queries WHERE id = ?", (query_id,))
    conn.commit()
    conn.close()
    return {"deleted": True, "id": query_id}