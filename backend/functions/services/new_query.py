from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import sqlite3
import uuid
from pathlib import Path
from backend.functions.services.ranking_pipeline import pipeline_from_text
from backend.functions.services.entity_linker import entity_linker_from_text

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "wikidata.db"


def save_query(title, hops, top_n, model):
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


def ensure_entity(cursor, qid, label=""):
    if label:
        cursor.execute("""
            INSERT INTO entities (qid, label) VALUES (?, ?)
            ON CONFLICT(qid) DO UPDATE SET label = excluded.label
            WHERE excluded.label != ''
        """, (qid, label))
    else:
        cursor.execute("""
            INSERT OR IGNORE INTO entities (qid, label) VALUES (?, ?)
        """, (qid, label))


def ensure_predicate(cursor, pid, label=""):
    if label:
        cursor.execute("""
            INSERT INTO predicates (pid, label) VALUES (?, ?)
            ON CONFLICT(pid) DO UPDATE SET label = excluded.label
            WHERE excluded.label != ''
        """, (pid, label))
    else:
        cursor.execute("""
            INSERT OR IGNORE INTO predicates (pid, label) VALUES (?, ?)
        """, (pid, label))


def save_query_results(query_id, results):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for item in results:
        for ent in item["entities"]:
            for r in ent["top_results"]:
                s = r["subject_qid"]
                p = r["predicate_pid"]
                o = r["object_qid"]
                s_l = r.get("subject_label", "")
                p_l = r.get("predicate_label", "")
                o_l = r.get("object_label", "")

                ensure_entity(cur, s, s_l)
                ensure_predicate(cur, p, p_l)
                ensure_entity(cur, o, o_l)

                cur.execute("""
                    INSERT INTO query_results (
                        query_id, subject_qid, predicate_pid, object_qid, triple, score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (query_id, s, p, o, r["triple"], r["score"]))

    conn.commit()
    conn.close()


@router.post("/new-query")
async def new_query(
    text: str = Body(...),
    hops: int = Body(...),
    top_n: int = Body(...),
    model: str = Body(default="spacy")
):
    print(f"model reçu : {model}")
    try:
        text = text.strip()
        if not text:
            return JSONResponse({"error": "Text cannot be empty"}, status_code=400)

        if model not in ["spacy", "bert", "rel", "all"]:
            return JSONResponse({"error": f"Modèle inconnu: {model}. Choisir parmi: spacy, bert, rel, all"}, status_code=400)

        print(f"QUERY: {text}")
        print(f"MODEL: {model}")

        qids = entity_linker_from_text(text, model=model)
        print(f"ENTITIES: {qids}")

        results = pipeline_from_text(text, qids, top_n=top_n)
        query_id = save_query(text[:200], hops, top_n, model)
        save_query_results(query_id, results)

        return {"status": "success", "query_id": query_id}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)