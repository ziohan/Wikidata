from fastapi import APIRouter
import sqlite3
from pathlib import Path
import math
from fastapi.responses import FileResponse
from backend.functions.services.graph_design import graph_design
import pandas as pd

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"
GRAPH_DIR = Path("./KG_papers_tree_layout")


@router.get("/search-entities")
def search_entities(
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    favorite: bool = False,
    sort_by: str = "occurrences",
    order: str = "desc"
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    offset = (page - 1) * page_size

    occurrences_subquery = """
        SELECT
            e.qid AS qid,
            COUNT(DISTINCT qr.query_id) AS occurrences
        FROM entities e
        LEFT JOIN query_results qr
            ON qr.subject_qid = e.qid
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

    cursor.execute(f"""
        SELECT
            e.qid,
            COALESCE(e.label, e.qid, 'Unknown'),
            COALESCE(o.occurrences, 0),
            CASE WHEN ef.qid IS NOT NULL THEN 1 ELSE 0 END as favorite
        {base_sql}
        {order_sql}
        LIMIT ? OFFSET ?
    """, params + [page_size, offset])

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


# ============================
# 🔥 NOVA FUNÇÃO: GRAPH DIRECTO
# ============================

@router.get("/entity-graph/{qid}")
def entity_graph(qid: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT subject_qid, predicate_pid, object_qid
            FROM triples
            WHERE subject_qid = ?
            LIMIT 100
        """, (qid,))

        triples = cursor.fetchall()
        conn.close()

        if not triples:
            return {"error": "No triples found"}

        structured = [[s, p, o] for s, p, o in triples]

        df = pd.DataFrame([{"Title": qid, "QID": qid}])

        graph_design(
            [qid],
            [structured],
            df,
            query_id=qid
        )

        return {
            "image_url": f"/graph/{qid}/png",
            "pdf_url": f"/graph/{qid}/pdf"
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/graph/{qid}/png")
def graph_png(qid: str):
    path = GRAPH_DIR / f"{qid}.png"
    if not path.exists():
        return {"error": "not found"}
    return FileResponse(path, media_type="image/png")


@router.get("/graph/{qid}/pdf")
def graph_pdf(qid: str):
    path = GRAPH_DIR / f"{qid}.pdf"
    if not path.exists():
        return {"error": "not found"}
    return FileResponse(path, media_type="application/pdf")