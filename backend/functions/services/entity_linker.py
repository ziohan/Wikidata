import spacy
import ast
import numpy as np
import pandas as pd
import requests
import time
import json
import os
from pathlib import Path
from .nlp_service import nlp

ENTITY_CACHE_FILE = "entity_cache.json"
WIKIPEDIA_TO_QID_CACHE_FILE = "wikipedia_qid_cache.json"

if os.path.exists(ENTITY_CACHE_FILE):
    with open(ENTITY_CACHE_FILE, "r", encoding="utf-8") as f:
        entity_cache = json.load(f)
else:
    entity_cache = {}

if os.path.exists(WIKIPEDIA_TO_QID_CACHE_FILE):
    with open(WIKIPEDIA_TO_QID_CACHE_FILE, "r", encoding="utf-8") as f:
        wikipedia_qid_cache = json.load(f)
else:
    wikipedia_qid_cache = {}

def save_entity_cache():
    with open(ENTITY_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(entity_cache, f, ensure_ascii=False)

def save_wikipedia_qid_cache():
    with open(WIKIPEDIA_TO_QID_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(wikipedia_qid_cache, f, ensure_ascii=False)

# ----------------------------------------------------------------
# Utilitaires communs
# ----------------------------------------------------------------

IGNORED_DESCRIPTIONS = [
    "article", "patent", "publication", "scholarly", "paper",
    "journal", "preprint", "book", "thesis", "dissertation",
    "conference", "proceedings", "review", "survey", "report",
    "chapter", "edit", "wikimedia", "wikipedia", "category",
    "template", "list of", "filed", "united states patent",
    "scholarly article", "scientific article", "review article",
    "published in", "written by", "authored by",
    "us patent", "eu patent", "scientific paper"
]

STOP_WORDS_EXTRA = {
    "these", "this", "the", "a", "an", "such", "multiple",
    "large", "specific", "limited", "similar", "various",
    "hierarchical", "labeled", "certain", "different", "new",
    "general", "common", "main", "key", "important"
}

def normalize_span(span_text, doc_span):
    tokens = [
        token.lemma_.lower()
        for token in doc_span
        if not token.is_stop
        and token.text.lower() not in STOP_WORDS_EXTRA
        and token.is_alpha
        and len(token.text) > 1
    ]
    if not tokens:
        return span_text.lower().strip()
    return " ".join(tokens)

def wikipedia_title_to_qid(title, retries=3, sleep_time=2):
    """Convertit un titre Wikipedia en QID Wikidata."""
    key = title.lower().strip()
    if key in wikipedia_qid_cache:
        return wikipedia_qid_cache[key]

    for attempt in range(retries):
        try:
            r = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbgetentities",
                    "sites": "enwiki",
                    "titles": title,
                    "props": "ids",
                    "format": "json"
                },
                headers={"User-Agent": "WikidataKGGenerator/1.0"},
                timeout=10
            )
            if not r.text.strip():
                raise Exception("Réponse vide")

            entities = r.json().get("entities", {})
            for entity_id, entity_data in entities.items():
                if entity_id != "-1":
                    wikipedia_qid_cache[key] = entity_id
                    save_wikipedia_qid_cache()
                    return entity_id

            wikipedia_qid_cache[key] = None
            save_wikipedia_qid_cache()
            return None

        except Exception as e:
            print(f"Wikipedia→QID tentative {attempt+1}/{retries} échouée pour '{title}': {e}")
            time.sleep(sleep_time * (attempt + 1))

    return None

def search_wikidata(span_text, doc_span=None, retries=3, sleep_time=2):
    """Cherche un QID Wikidata via l'API de recherche."""
    normalized = normalize_span(span_text, doc_span) if doc_span else span_text.lower().strip()
    key = normalized

    if key in entity_cache:
        return entity_cache[key]

    for attempt in range(retries):
        try:
            r = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "search": normalized,
                    "language": "en",
                    "format": "json",
                    "limit": 5
                },
                headers={"User-Agent": "WikidataKGGenerator/1.0"},
                timeout=10
            )
            if not r.text.strip():
                raise Exception("Réponse vide")

            results = r.json().get("search", [])
            for result in results:
                description = result.get("description", "").lower()
                label = result.get("label", "").lower()

                if any(x in description for x in IGNORED_DESCRIPTIONS):
                    continue

                span_words = set(key.split())
                label_words = set(label.split())
                if len(span_words) > 1 and not span_words.intersection(label_words):
                    continue

                qid = result["id"]
                entity_cache[key] = qid
                save_entity_cache()
                return qid

            entity_cache[key] = None
            save_entity_cache()
            return None

        except Exception as e:
            print(f"Wikidata search tentative {attempt+1}/{retries} échouée pour '{normalized}': {e}")
            time.sleep(sleep_time * (attempt + 1))

    return None

# ----------------------------------------------------------------
# Modèle 1 : SpaCy + Wikidata Search API (actuel)
# ----------------------------------------------------------------

def entity_linker_spacy(text):
    """Détection via SpaCy NER + noun chunks + Wikidata Search API."""
    doc = nlp(str(text))
    spans = []

    for ent in doc.ents:
        spans.append((ent.text, ent))

    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:
            spans.append((chunk.text, chunk))

    seen = set()
    unique_spans = []
    for s, doc_span in spans:
        clean = s.strip().lower()
        if clean not in seen and len(clean) > 2:
            seen.add(clean)
            unique_spans.append((s.strip(), doc_span))

    qids = []
    seen_qids = set()
    for span, doc_span in unique_spans:
        qid = search_wikidata(span, doc_span)
        if qid and qid not in seen_qids:
            seen_qids.add(qid)
            qids.append(qid)
        time.sleep(0.3)

    print(f"[SpaCy] Entities found: {qids}")
    return qids

# ----------------------------------------------------------------
# Modèle 2 : BERT NER + Wikidata Search API
# ----------------------------------------------------------------

_bert_ner_pipeline = None

def get_bert_pipeline():
    """Charge le modèle BERT NER (singleton)."""
    global _bert_ner_pipeline
    if _bert_ner_pipeline is None:
        print("Chargement du modèle BERT NER...")
        from transformers import pipeline
        _bert_ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        print("Modèle BERT NER chargé !")
    return _bert_ner_pipeline

def entity_linker_bert(text):
    """Détection via BERT NER + Wikidata Search API."""
    ner = get_bert_pipeline()
    entities = ner(str(text))

    seen = set()
    qids = []
    seen_qids = set()

    for ent in entities:
        span = ent["word"].strip()
        score = ent["score"]

        # Filtre les entités avec un score trop bas
        if score < 0.7:
            continue

        clean = span.lower()
        if clean in seen or len(clean) <= 2:
            continue
        seen.add(clean)

        print(f"[BERT] Entité détectée: {span} ({ent['entity_group']}, score={score:.2f})")

        qid = search_wikidata(span)
        if qid and qid not in seen_qids:
            seen_qids.add(qid)
            qids.append(qid)
        time.sleep(0.3)

    print(f"[BERT] Entities found: {qids}")
    return qids

# ----------------------------------------------------------------
# Modèle 3 : REL (Radboud Entity Linker) via API REST
# ----------------------------------------------------------------

def entity_linker_rel(text, retries=3, sleep_time=2):
    """Détection via l'API REST REL + conversion Wikipedia → QID."""
    for attempt in range(retries):
        try:
            r = requests.post(
                "https://rel.cs.ru.nl/api",
                json={"text": str(text), "spans": []},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if r.status_code != 200:
                raise Exception(f"Status {r.status_code}")

            results = r.json()
            break

        except Exception as e:
            print(f"REL tentative {attempt+1}/{retries} échouée: {e}")
            time.sleep(sleep_time * (attempt + 1))
            results = []

    qids = []
    seen_qids = set()

    for result in results:
        # Format REL: [position, longueur, texte, label_wikipedia, score_mention, score_entité, type_NER]
        if len(result) < 6:
            continue

        span_text = result[2]
        wikipedia_title = result[3]
        mention_score = result[4]
        entity_score = result[5]

        # Filtre les entités avec un score trop bas
        if entity_score < 0.7:
            print(f"[REL] Ignoré (score faible): {span_text} → {wikipedia_title} ({entity_score:.2f})")
            continue

        print(f"[REL] Entité: {span_text} → {wikipedia_title} (score={entity_score:.2f})")

        # Convertit le titre Wikipedia en QID Wikidata
        qid = wikipedia_title_to_qid(wikipedia_title)
        if qid and qid not in seen_qids:
            seen_qids.add(qid)
            qids.append(qid)
        time.sleep(0.3)

    print(f"[REL] Entities found: {qids}")
    return qids

# ----------------------------------------------------------------
# Merge des résultats
# ----------------------------------------------------------------

def merge_qids(*qid_lists):
    """
    Fusionne les QID de plusieurs modèles en évitant les doublons.
    Les QID présents dans plusieurs modèles sont prioritaires.
    """
    from collections import Counter
    all_qids = [qid for qids in qid_lists for qid in qids]
    counts = Counter(all_qids)

    # Trie par fréquence (QID détectés par plusieurs modèles en premier)
    sorted_qids = sorted(counts.keys(), key=lambda q: -counts[q])
    print(f"[Merge] QIDs fusionnés: {sorted_qids}")
    return sorted_qids

# ----------------------------------------------------------------
# Fonction principale
# ----------------------------------------------------------------

def entity_linker_from_text(text, model="spacy"):
    """
    Détecte les entités selon le modèle choisi.
    model: "spacy" | "bert" | "rel" | "all"
    """
    print(f"Modèle sélectionné: {model}")

    if model == "spacy":
        return entity_linker_spacy(text)

    elif model == "bert":
        return entity_linker_bert(text)

    elif model == "rel":
        return entity_linker_rel(text)

    elif model == "all":
        # Utilise tous les modèles et merge les résultats
        print("Utilisation de tous les modèles...")
        spacy_qids = entity_linker_spacy(text)
        bert_qids = entity_linker_bert(text)
        rel_qids = entity_linker_rel(text)
        return merge_qids(spacy_qids, bert_qids, rel_qids)

    else:
        print(f"Modèle inconnu '{model}', utilisation de SpaCy par défaut")
        return entity_linker_spacy(text)

# ----------------------------------------------------------------
# Fonctions originales conservées pour compatibilité
# ----------------------------------------------------------------

def entites(text):
    doc = nlp(str(text))
    return doc._.linkedEntities

def entity_linker(data):
    data.head()
    data["EntityLinked"] = data["Title"].apply(entites)
    data["QID"] = data["EntityLinked"].apply(lambda ents: [ent.get_id() for ent in ents])
    data["Labels"] = data["EntityLinked"].apply(lambda ents: [ent.get_label() for ent in ents])
    data.head()
    liste1_qids = data['QID'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x).tolist()
    liste1 = np.concatenate(liste1_qids)
    listesansnul = [int(item) for item in liste1 if item is not None]
    UniqueList = np.unique(listesansnul)
    UniqueList2 = UniqueList.tolist()
    UniqueList3 = [f"Q{id}" if not str(id).startswith("Q") else id for id in UniqueList2]
    print(len(UniqueList3))
    return UniqueList3