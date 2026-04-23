import spacy
import spacy_entity_linker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from SPARQLWrapper import SPARQLWrapper, JSON

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_md")
nlp.add_pipe("entityLinker", last=True)

class AnalyzeRequest(BaseModel):
    text: str
    max_triples_per_entity: int = 5

@app.get("/health")
def health():
    return {"status": "ok"}

def extract_triples_for_qid(qid: str, subject_label: str, limit: int = 5):
    query = f"""
    SELECT ?pLabel ?oLabel WHERE {{
      wd:{qid} ?p ?o .
      FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/P"))
      FILTER(STRSTARTS(STR(?o), "http://www.wikidata.org/entity/Q"))
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    LIMIT {limit}
    """

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(60)
    results = sparql.query().convert()

    triples = []
    for row in results["results"]["bindings"]:
        predicate = row.get("pLabel", {}).get("value", "")
        obj = row.get("oLabel", {}).get("value", "")
        if predicate and obj:
            triples.append({
                "subject": subject_label,
                "predicate": predicate,
                "object": obj
            })
    return triples

@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    doc = nlp(payload.text)
    linked_entities = doc._.linkedEntities

    seen = set()
    entities = []

    for ent in linked_entities:
        qid = str(ent.get_id())
        label = ent.get_label()

        if not qid or not label:
            continue

        if not qid.startswith("Q"):
            qid = f"Q{qid}"

        if qid in seen:
            continue
        seen.add(qid)

        triples = extract_triples_for_qid(qid, label, payload.max_triples_per_entity)

        entities.append({
            "qid": qid,
            "label": label,
            "triples": triples
        })

    return {"entities": entities}