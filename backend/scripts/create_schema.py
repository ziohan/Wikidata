import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "wikidata.db"

def create_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Entities - qids
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entities (
        qid TEXT PRIMARY KEY,
        label TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queries (
        id TEXT PRIMARY KEY,
        title TEXT,
        hops INTEGER,
        top_n INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_id TEXT NOT NULL,
        triple TEXT NOT NULL,
        score REAL NOT NULL,

        FOREIGN KEY(query_id) REFERENCES queries(id)
    )
    """)
    # Predicates - pids
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predicates (
        pid TEXT PRIMARY KEY,
        label TEXT
    )
    """)

    # Triples
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_qid TEXT NOT NULL,
        predicate_pid TEXT NOT NULL,
        object_qid TEXT,
        object_value TEXT,

        FOREIGN KEY(subject_qid) REFERENCES entities(qid),
        FOREIGN KEY(predicate_pid) REFERENCES predicates(pid),
        FOREIGN KEY(object_qid) REFERENCES entities(qid),

        CHECK (
            (object_qid IS NOT NULL AND object_value IS NULL) OR
            (object_qid IS NULL AND object_value IS NOT NULL)
        )
    )
    """)

    # Entity cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entity_cache (
        qid TEXT PRIMARY KEY,
        fully_loaded INTEGER DEFAULT 0,
        last_updated TEXT,
        triplet_count INTEGER DEFAULT 0
    )
    """)

    # INDEXES FOR PERFORMANCE

    # looks for a subject
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_triples_subject
    ON triples(subject_qid)
    """)

    # looks for a predicate
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_triples_predicate
    ON triples(predicate_pid)
    """)

    # looks for an object
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_triples_object_qid
    ON triples(object_qid)
    """)

    # fast lookup cache QIDs
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_cache_qid
    ON entity_cache(qid)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_query_results_query_id
    ON query_results(query_id)
    """)

    conn.commit()
    conn.close()
    print("Database schema + indexes created successfully.")

if __name__ == "__main__":
    create_schema()