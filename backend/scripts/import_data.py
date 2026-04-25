import sqlite3
import pandas as pd
from pathlib import Path
from backend.functions.services.entity_linker import entity_linker
from backend.functions.services.extract_triples import extracttriples, est_triplet_valide

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "wikidata.db"
CSV_PATH = BASE_DIR / "data" / "csv" / "DBLP1_processed_.csv"

def get_conn():
    return sqlite3.connect(DB_PATH)

def insert_entity(cursor, qid, label=""):
    cursor.execute("""
        INSERT OR IGNORE INTO entities (qid, label)
        VALUES (?, ?)
    """, (qid, label))

def insert_predicate(cursor, pid, label=""):
    cursor.execute("""
        INSERT OR IGNORE INTO predicates (pid, label)
        VALUES (?, ?)
    """, (pid, label))

def insert_triple(cursor, s, p, o):
    cursor.execute("""
        INSERT INTO triples (subject_qid, predicate_pid, object_qid, object_value)
        VALUES (?, ?, ?, NULL)
    """, (s, p, o))

def update_cache(cursor, qid, count):
    cursor.execute("""
        INSERT OR REPLACE INTO entity_cache (qid, fully_loaded, last_updated, triplet_count)
        VALUES (?, 1, datetime('now'), ?)
    """, (qid, count))

def import_data():
    conn = get_conn()
    cursor = conn.cursor()
    data = pd.read_csv(CSV_PATH, sep=";")

    print("Running entity linker...")
    qids = entity_linker(data)
    print(f"Total QIDs: {len(qids)}")

    for i, qid in enumerate(qids):
        print(f"\n[{i}] Processing {qid}")

        try:
            triples = extracttriples(qid)
        except Exception as e:
            print("SPARQL error:", e)
            continue

        valid_triples = [t for t in triples if est_triplet_valide(t)]
        update_cache(cursor, qid, len(valid_triples))

        for s, p, o in valid_triples:
            # entities
            insert_entity(cursor, s)
            insert_entity(cursor, o)

            # predicate
            insert_predicate(cursor, p)

            # triple
            insert_triple(cursor, s, p, o)

        conn.commit()
        print(f"{qid}: {len(valid_triples)} triples inserted")
    conn.close()
    print("\nImport finished!")

if __name__ == "__main__":
    import_data()