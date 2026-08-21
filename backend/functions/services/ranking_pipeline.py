import pandas as pd
import ast
import sqlite3
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from backend.functions.services.extract_triples import (extracttriples, est_triplet_valide, recuperer_labels_batch)

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "backend" / "data" / "wikidata.db"

bi_model = SentenceTransformer("all-mpnet-base-v2")
cross_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def conn():
    return sqlite3.connect(DB_PATH)

def get_triples(qid):
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT subject_qid, predicate_pid, object_qid
            FROM triples
            WHERE subject_qid = ?
        """, (qid,))
        return cur.fetchall()

def save_triples(qid, triples):
    with conn() as c:
        cur = c.cursor()

        # subject, predicate, object
        for s, p, o in triples:
            if s != qid:
                continue

            cur.execute("""
                INSERT OR IGNORE INTO triples
                (subject_qid, predicate_pid, object_qid, object_value)
                VALUES (?, ?, ?, NULL)
            """, (s, p, o))
        c.commit()

# Extract all the unique IDs from the triplets
def fetch_qid(qid):
    triples = get_triples(qid)
    if not triples:
        try:
            raw = extracttriples(qid)
        except:
            return []

        triples = [t for t in raw if est_triplet_valide(t)]
        save_triples(qid, triples)

    return [t for t in triples if t[0] == qid]

def predicate_weight(p):
    p = p.lower()

    if any(k in p for k in ["use", "apply", "based on", "develop", "affect", "cause", "study", "model"]):
        return 1.25
    if any(k in p for k in ["part of", "has", "related", "contains"]):
        return 1.10
    if any(k in p for k in ["instance of", "subclass of"]):
        return 0.85
    if any(k in p for k in [
        "wikimedia", "template", "category", "described by source", "focus list", "maintained by", "same as", "coincident", "outline", "topic"
    ]):
        return 0.60

    return 1.0

def build_triples(qids):
    all_triples = []
    all_ids = set()
    for qid in qids:
        triples = fetch_qid(qid)
        for s, p, o in triples:
            all_triples.append((s, p, o))
            all_ids.update([s, p, o])

    if not all_triples:
        return []

    # Fetch labels for all unique IDs in one batch to minimize database calls
    labels = recuperer_labels_batch(list(all_ids))

    results = []
    seen = set()

    # Build the final list of triples with labels
    for s, p, o in all_triples:
        s_l = labels.get(s, "")
        p_l = labels.get(p, "")
        o_l = labels.get(o, "")

        raw = f"{s_l} | {p_l} | {o_l}"
        if raw in seen:
            continue
        seen.add(raw)

        embed = f"{s_l} -- {p_l} --> {o_l}"
        results.append({
            "raw": raw,
            "embed": embed,
            "predicate": p_l,
            "subject": s_l,
            "object": o_l,
            "subject_qid": s,
            "predicate_pid": p,
            "object_qid": o,
        })

    return results

def minmax(x):
    x = np.array(x)
    return (x - x.min()) / (x.max() - x.min() + 1e-8)

def rank(title, triples, top_n=10):
    if not triples:
        return []
    
    embeds = [t["embed"] for t in triples]
    predicates = [t["predicate"] for t in triples]
    subjects = [t["subject"] for t in triples]
    objects = [t["object"] for t in triples]

    # Here we can compute the embeddings for the title and the triples using the bi-encoder
    title_emb = bi_model.encode([title])
    triple_emb = bi_model.encode(embeds)

    cosine_scores = cosine_similarity(title_emb, triple_emb)[0]

    # Here we can compute the entity relevance scores based on the subject and object embeddings
    subj_emb = bi_model.encode(subjects)
    obj_emb = bi_model.encode(objects)

    # We take the maximum similarity between the title and either the subject or object as the entity score
    subj_scores = cosine_similarity(title_emb, subj_emb)[0]
    obj_scores = cosine_similarity(title_emb, obj_emb)[0]

    # We take the maximum of subject and object scores to get a single entity relevance score for each triple
    entity_scores = np.maximum(subj_scores, obj_scores)

    # Here we use the cross-encoder to get a more fine-grained relevance score for each triple given the title
    pairs = [(title, t["raw"]) for t in triples]
    cross_scores = cross_model.predict(pairs)

    # Normalize all scores
    cross_scores = minmax(cross_scores)
    cosine_scores = minmax(cosine_scores)
    entity_scores = minmax(entity_scores)

    # Saving the scores for debugging
    final_scores = []

    for i in range(len(triples)):
        base = (
            0.45 * cosine_scores[i] +
            0.35 * cross_scores[i] +
            0.20 * entity_scores[i]
        )

        # We can give more weight to certain predicates that are more relevant for the title
        weight = 0.75 + 0.25 * predicate_weight(predicates[i])
        score = base * weight
        final_scores.append(score)
    idx = np.argsort(final_scores)[::-1][:top_n]
    return [(
        triples[i]["raw"],
        float(final_scores[i]),
        triples[i]["subject_qid"],
        triples[i]["predicate_pid"],
        triples[i]["object_qid"],
        triples[i]["subject"],
        triples[i]["predicate"],
        triples[i]["object"],
    ) for i in idx]

def pipeline_from_text(text, qids, top_n=10):
    entity_results = []
    print(f"\nQUERY: {text}")

    for qid in qids:
        print(f"\nENTITY {qid}")
        triples = build_triples([qid])
        ranked = rank(text, triples, top_n=top_n)
        print(f"Top {top_n} triples:\n")
        for i, (t, s, sq, pp, oq, s_l, p_l, o_l) in enumerate(ranked, 1):
            print(f"{i:02d} - {s:.4f} | {t}")

        entity_results.append({
            "qid": qid,
            "triples_used": len(triples),
            "top_results": [
                {
                    "triple": t,
                    "score": s,
                    "subject_qid": sq,
                    "predicate_pid": pp,
                    "object_qid": oq,
                    "subject_label": s_l,
                    "predicate_label": p_l,
                    "object_label": o_l,
                }
                for t, s, sq, pp, oq, s_l, p_l, o_l in ranked
            ]
        })

    return [{
        "title": text,
        "entities": entity_results
    }]

def pipeline(csv_path, top_n=10):
    df = pd.read_csv(csv_path, sep=";")

    all_results = []

    for _, row in df.iterrows():
        title = row["Title"]

        try:
            qids = ast.literal_eval(row["QID"])
        except:
            raise ValueError(f"Erro ao parsear QID: {row['QID']}")

        qids = [f"Q{x}" if not str(x).startswith("Q") else x for x in qids]

        entity_results = []
        print(f"\nQUERY: {title}")

        for qid in qids:
            print(f"\nENTITY {qid}")
            triples = build_triples([qid])
            ranked = rank(title, triples, top_n=top_n)
            print(f"Top {top_n} triples:\n")
            for i, (t, s, sq, pp, oq, s_l, p_l, o_l) in enumerate(ranked, 1):
                print(f"{i:02d} - {s:.4f} | {t}")

            entity_results.append({
                "qid": qid,
                "triples_used": len(triples),
                "top_results": [
                    {
                        "triple": t,
                        "score": s,
                        "subject_qid": sq,
                        "predicate_pid": pp,
                        "object_qid": oq,
                        "subject_label": s_l,
                        "predicate_label": p_l,
                        "object_label": o_l,
                    }
                    for t, s, sq, pp, oq, s_l, p_l, o_l in ranked
                ]
            })
        all_results.append({
            "title": title,
            "entities": entity_results
        })

    return all_results

if __name__ == "__main__":
    path = BASE_DIR / "backend" / "data" / "csv" / "test_dblp.csv"
    pipeline(path)