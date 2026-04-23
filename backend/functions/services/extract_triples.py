import pandas as pd
import os
import json
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import re
# #Extraction triplets labels
from tqdm import tqdm

CACHE_FILE = "triplet_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        triplet_cache = json.load(f)
else:
    triplet_cache = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(triplet_cache, f)

def extracttriples(qid, max_triples=3000, batch_size = 200, retries=3, sleep_time=1.5, timeout = 60):
    if qid in triplet_cache:
        return triplet_cache[qid]

    all_triplets = []
    seen = set()
    offset = 0

    while len(all_triplets) < max_triples:
      limit = min(max_triples - len(all_triplets), batch_size)
      query = f"""
      SELECT ?p ?o WHERE {{
        wd:{qid} ?p ?o .
        FILTER(STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/P"))
        FILTER(STRSTARTS(STR(?o), "http://www.wikidata.org/entity/Q"))
      }}
      LIMIT {limit}
      OFFSET {offset}
      """
      success = False

      for attempt in range(retries):
          try:
              sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
              sparql.setQuery(query)
              sparql.setReturnFormat(JSON)
              sparql.setTimeout(timeout)
              sparql.addCustomHttpHeader("User-Agent", "FatimaWikidataProject/1.0")
              results = sparql.query().convert()

              triplets = []


              for b in results["results"]["bindings"]:
                  p = b["p"]["value"].split("/")[-1]
                  o = b["o"]["value"].split("/")[-1]
                  if (qid, p, o) not in seen:
                    seen.add((qid, p, o))
                    triplets.append((qid, p, o))

              all_triplets.extend(triplets)

              print(f"{qid} | OFFSET={offset} | +{len(triplets)} triplets | total = {len(all_triplets)}")

              success = True
              time.sleep(sleep_time)
              break

          except Exception as e:
              print(f"Tentative {attempt+1} échouée pour {qid}: {e}")
              time.sleep(3)
      if not success:
        print(f"Aucun résultat trouvé pour {qid} à partir de OFFSET={offset}")
        print(f"Fin atteinte pour {qid}")
        break;

      if (len(all_triplets) >= max_triples) or len(triplets) < limit:
        print(f"Fin atteinte pour {qid}")
        break;

      offset += limit

    triplet_cache[qid] = all_triplets
    save_cache()
    return all_triplets

# vérifier si les triplets extraits sont valides
def est_triplet_valide(triplet):
    def est_valide(chaine):
        if not isinstance(chaine, str) or not chaine.strip():
            return False
        if re.search(r'http|\.jpg|\.png|\.webm|\.ogg|\.opus|\.mp4$', chaine, re.IGNORECASE):
            return False
        if re.search(r'[^a-zA-Z0-9]', chaine):  # caractères spéciaux autres que lettres/chiffres
            return False
        return True

    if len(triplet) != 3:
        return False
    return all(est_valide(elem) for elem in triplet)


# ---- Étape 1 : Extraire toutes les entités uniques d'une liste de triplets ----
def extraire_ids_unique(triplets):
    ids = set()
    for (s, p, o) in triplets:
        ids.update([s, p, o])
    return list(ids)

# ---- Étape 2 : Récupérer tous les labels en une seule requête SPARQL ----
def recuperer_labels_batch(entites):
    entites = [e for e in entites if e]  # filtre chaînes vides
    entites_str = " ".join(f"wd:{e}" for e in entites)

    query = f"""
    SELECT ?entite ?entiteLabel WHERE {{
      VALUES ?entite {{ {entites_str} }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    """

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='OlafJanssen from PAWS')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    labels = {}
    for result in results["results"]["bindings"]:
        qid = result["entite"]["value"].split("/")[-1]
        label = result.get("entiteLabel", {}).get("value", "")
        labels[qid] = label
    return labels

# ---- Étape 3 : Appliquer les labels à chaque triplet ----
def get_labels_triplets_batch(triplets):
    ids = extraire_ids_unique(triplets)
    labels = recuperer_labels_batch(ids)

    triplets_labels = []
    for s, p, o in triplets:
        label_s = labels.get(s, "")
        label_p = labels.get(p, "")
        label_o = labels.get(o, "")
        if label_s and label_p and label_o:
            triplets_labels.append((label_s, label_p, label_o))
    return triplets_labels

# ---- Étape 4 (optionnelle) : Diviser par lots si les listes sont trop longues ----
def decouper_par_batch(liste, taille):
    for i in range(0, len(liste), taille):
        yield liste[i:i+taille]

def extract_triples(UniqueList3):
    #ordering the printing of the list of QIDs
    for k, id in enumerate(UniqueList3):
        print("index =", k, "QID =", id)
    
    #Extracting triples for the first 50 QIDs
    listtripleids = []
    sample_qids = UniqueList3[:50]

    for k, qid in enumerate(sample_qids):
        print("k :", k, "|", qid)
        triples = extracttriples(qid)
        print("Triples extracted for", qid, ":", len(triples),"\n\n")
        listtripleids.append(triples)

    # Printing the first 5 triplets for the first QID
    print(listtripleids[0][:5])
    # Printing the number of triplets extracted for the first QID
    print(sample_qids[0], "->", len(listtripleids[0]), "triplets")

    all_triples = [triple for sublist in listtripleids for triple in sublist]

    # Printing the total number of triplets extracted for the 50 QIDs
    print("Nombre total de triplets :", len(all_triples))
    # Printing the first 5 triplets extracted for the 50 QIDs
    print(all_triples[:5])

    # Printing the first 5 triplets in a DataFrame format
    triples_df = pd.DataFrame(all_triples, columns=["subject", "predicate", "object"])
    print(triples_df.head())

    # Filtering out invalid triplets
    for lt, triplet_list in enumerate(listtripleids):
        print('lt:', lt)
        triplets_valides = []
        for k, triplet in enumerate(triplet_list):
            if est_triplet_valide(triplet):
                triplets_valides.append(triplet)
        listtripleids[lt] = triplets_valides

    # Printing the number of triplets after filtering
    all_triples = [t for sub in listtripleids for t in sub]
    print("Nombre de triplets après filtrage :", len(all_triples))

    # Printing the first 5 triplets after filtering in a DataFrame format
    triples_df = pd.DataFrame(all_triples, columns=["subject", "predicate", "object"])
    print(triples_df.head())

    # Adding a new column that concatenates the predicate and object for easier labeling
    triples_df["rel_obj"] = triples_df["predicate"] + "_" + triples_df["object"]
    print(triples_df.head())

    # ---- Utilisation sur liste de listes de triplets ----
    listtripletslabel = []
    for triplet_list in tqdm(listtripleids):
        triplets_labels = []
        for sous_liste in decouper_par_batch(triplet_list, 200):
            triplets_labels.extend(get_labels_triplets_batch(sous_liste))
        listtripletslabel.append(triplets_labels)

    # Printing the first 5 labeled triplets for the first QID
    print(listtripletslabel[0][:5])

    # Unifying all labeled triplets into a single list
    all_labeled_triples = [t for sub in listtripletslabel for t in sub]

    print("Nombre total de triplets labelisés :", len(all_labeled_triples))
    # Printing the first 5 labled triplets in a a list format
    print(all_labeled_triples[:5])

    # Printing the first 5 labled triplets in a DataFrame format
    triples_labels_df = pd.DataFrame(
        all_labeled_triples,
        columns=["subject_label", "predicate_label", "object_label"]
    )
    print(triples_labels_df.head())

    # Adding a new column that concatenates the subject, predicate and object labels for easier graph design
    triples_labels_df["triple_text"] = (
        triples_labels_df["subject_label"] + " "
        + triples_labels_df["predicate_label"] + " "
        + triples_labels_df["object_label"]
    )
    print(triples_labels_df.head())

    return triples_labels_df, listtripletslabel