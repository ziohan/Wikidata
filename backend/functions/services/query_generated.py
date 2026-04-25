from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
import sqlite3
from pathlib import Path
import pandas as pd
from backend.functions.services.graph_design import graph_design

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"
GRAPH_DIR = Path("./KG_papers_tree_layout")
    
def parse_triple(triple_str: str):
    parts = triple_str.split()
    if len(parts) < 3:
        return None

    subject = parts[0]
    obj = parts[-1]
    predicate = " ".join(parts[1:-1])
    return [subject, predicate, obj]

@router.get("/query-generated/{query_id}")
def get_query_generated(query_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, hops, top_n
            FROM queries
            WHERE id = ?
        """, (query_id,))
        query = cursor.fetchone()

        if not query:
            return JSONResponse({"error": "Query não encontrada"}, status_code=404)

        title, hops, top_n = query
        cursor.execute("""
            SELECT triple, score
            FROM query_results
            WHERE query_id = ?
            ORDER BY score DESC
        """, (query_id,))
        triples = cursor.fetchall()
        conn.close()

        triples_list = []
        structured_triples = []
        for triple_str, score in triples:
            triples_list.append({
                "triple": triple_str,
                "score": score
            })
            parsed = parse_triple(triple_str)
            if parsed:
                structured_triples.append(parsed)

        UniqueList3 = ["Q1"]
        listtripletslabel = [structured_triples]

        df = pd.DataFrame([{
            "Title": title,
            "QID": "Q1"
        }])

        graph_design(
            UniqueList3,
            listtripletslabel,
            df,
            query_id=query_id
        )

        return {
            "query_id": query_id,
            "title": title,
            "hops": hops,
            "top_n": top_n,
            "triples": triples_list,

            "image_url": f"/graph/{query_id}/png",
            "download_png": f"/graph/{query_id}/png",
            "download_pdf": f"/graph/{query_id}/pdf"
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/graph/{query_id}/png")
def get_graph_png(query_id: str):
    path = GRAPH_DIR / f"{query_id}.png"
    if not path.exists():
        return JSONResponse({"error": "Imagem não encontrada"}, status_code=404)

    return FileResponse(
        path,
        media_type="image/png",
        filename=f"{query_id}.png"
    )

@router.get("/graph/{query_id}/pdf")
def get_graph_pdf(query_id: str):
    path = GRAPH_DIR / f"{query_id}.pdf"
    if not path.exists():
        return JSONResponse({"error": "PDF não encontrado"}, status_code=404)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{query_id}.pdf"
    )