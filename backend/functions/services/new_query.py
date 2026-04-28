from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import tempfile
from pathlib import Path
import pandas as pd
import sqlite3
import uuid
from backend.functions.services.ranking_pipeline import pipeline

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"

def validate_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep=";")
    except Exception:
        return False, "Erro ao ler CSV"
    required_cols = {"Title", "QID"}
    if not required_cols.issubset(df.columns):
        return False, f"CSV deve conter colunas: {required_cols}"

    return True, None

def save_query(title, hops, top_n):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO queries (id, title, hops, top_n)
        VALUES (?, ?, ?, ?)
    """, (query_id, title, hops, top_n))

    conn.commit()
    conn.close()

    return query_id

def save_query_results(query_id, results):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for item in results:
        for r in item["top_results"]:
            cur.execute("""
                INSERT INTO query_results (
                    query_id,
                    subject_qid,
                    predicate_pid,
                    object_qid,
                    triple,
                    score
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                query_id,
                r["subject_qid"],
                r["predicate_pid"],
                r["object_qid"],
                r["triple"],
                r["score"]
            ))
    conn.commit()
    conn.close()

@router.post("/new-query")
async def new_query(
    file: UploadFile = File(...),
    hops: int = Form(...),
    top_n: int = Form(...)
):
    try:
        if not file.filename.endswith(".csv"):
            return JSONResponse({"error": "Arquivo deve ser CSV"}, status_code=400)
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / file.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        valid, error = validate_csv(temp_path)
        if not valid:
            return JSONResponse({"error": error}, status_code=400)

        results = pipeline(str(temp_path), top_n=top_n)
        title = results[0]["title"] if results else "unknown"

        query_id = save_query(title, hops, top_n)
        save_query_results(query_id, results)

        return {
            "status": "success",
            "query_id": query_id
        }

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)