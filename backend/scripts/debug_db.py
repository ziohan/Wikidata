import sqlite3
from pathlib import Path
import pandas as pd
import ast

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "wikidata.db"
CSV_PATH = BASE_DIR / "data" / "csv" / "test_dblp.csv"

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_qids_from_csv():
    df = pd.read_csv(CSV_PATH, sep=";")

    print("\nCSV SAMPLE:")
    print(df.head(1))

    # convert string representation of list to actual list
    qids_raw = df["QID"].iloc[0]
    qids = ast.literal_eval(qids_raw)

    # garantee that all IDs are in the format "Q____"
    qids = [f"Q{id}" if not str(id).startswith("Q") else id for id in qids]

    return qids

# Check all the entities from the CSV in the database and print how many are found vs not found
def check_entities_in_db(cursor, qids):
    print("\nCHECKING CSV ENTITIES IN DB:")

    found = []
    not_found = []

    for qid in qids:
        cursor.execute("SELECT qid FROM entities WHERE qid = ?", (qid,))
        result = cursor.fetchone()

        if result:
            found.append(qid)
        else:
            not_found.append(qid)

    print(f"Found in DB: {len(found)}")
    print(f"Not found: {len(not_found)}")

    print("\nFOUND:")
    print(found[:10])

    print("\nNOT FOUND:")
    print(not_found[:10])

    return found

# Print the first 5 triples for each of the first 3 QIDs found in the database
def print_triples_for_qids(cursor, qids):
    print("\nTRIPLES FOR CSV ENTITIES:\n")

    # sets a limit of 3 QIDs for demonstration
    for qid in qids[:3]:
        print(f"\nEntity: {qid}")

        cursor.execute("""
            SELECT subject_qid, predicate_pid, object_qid
            FROM triples
            WHERE subject_qid = ?
            LIMIT 5
        """, (qid,))

        triples = cursor.fetchall()

        if not triples:
            print("  No triples found")
        else:
            for t in triples:
                print(" ", t)

def main():
    conn = get_conn()
    cursor = conn.cursor()

    # get the list of QIDs from the CSV file
    csv_qids = get_qids_from_csv()

    # check which of these QIDs are present in the database and get the list of found QIDs
    found_qids = check_entities_in_db(cursor, csv_qids)

    # print the first 5 triples for each of the first 3 QIDs found in the database
    print_triples_for_qids(cursor, found_qids)
    conn.close()

if __name__ == "__main__":
    main()