import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "backend" / "data" / "wikidata.db"


def conn():
    return sqlite3.connect(DB_PATH)

def test_counts():
    print("\nDATABASE STATISTICS:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM entities")
        entities_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM predicates")
        predicates_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM triples")
        triples_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT subject_qid)
            FROM triples
        """)
        subjects_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT object_qid)
            FROM triples
            WHERE object_qid IS NOT NULL
        """)
        objects_count = cur.fetchone()[0]

        print(f"Entities:   {entities_count}")
        print(f"Predicates: {predicates_count}")
        print(f"Triples:    {triples_count}")
        print(f"Subjects:   {subjects_count}")
        print(f"Objects:    {objects_count}")


def test_schema():
    print("\nCHECK TABLES:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        print("Tables:", tables)
        required = [
            "entities",
            "queries",
            "query_results",
            "triples",
            "predicates",
            "entity_favorites"
        ]
        for t in required:
            print(f"{t}: {'OK' if t in tables else 'MISSING'}")


def test_entities():
    print("\nSAMPLE ENTITIES:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("SELECT qid, label FROM entities LIMIT 5")
        rows = cur.fetchall()
        for r in rows:
            print(r)


def test_queries():
    print("\nSAMPLE QUERIES:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT id, title, hops, top_n, created_at
            FROM queries
            ORDER BY created_at DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        for r in rows:
            print(r)


def test_query_results():
    print("\nQUERY RESULTS SAMPLE:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT query_id, subject_qid, predicate_pid, object_qid, score
            FROM query_results
            LIMIT 10
        """)
        rows = cur.fetchall()
        for r in rows:
            print(r)


def test_triples():
    print("\nTRIPLES SAMPLE:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT subject_qid, predicate_pid, object_qid
            FROM triples
            LIMIT 10
        """)
        rows = cur.fetchall()
        for r in rows:
            print(r)


def test_favorites():
    print("\nFAVORITES:")
    with conn() as c:
        cur = c.cursor()
        cur.execute("""
            SELECT qid FROM entity_favorites
        """)
        rows = cur.fetchall()
        print("Favorites:", [r[0] for r in rows])


def main():
    print("DATABASE INTEGRATION TEST:")
    test_counts()
    test_schema()
    test_entities()
    test_queries()
    test_query_results()
    test_triples()
    test_favorites()
    print("\nDONE")

if __name__ == "__main__":
    main()