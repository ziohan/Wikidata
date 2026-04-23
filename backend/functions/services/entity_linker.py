import spacy
import ast
import numpy as np
import pandas as pd
from pathlib import Path
from .nlp_service import nlp

#Extraction entités
def entites(text):
    doc = nlp(str(text))
    return doc._.linkedEntities

def entity_linker(data):
    data.head()
    data["EntityLinked"] = data["Title"].apply(entites)
    data["QID"] = data["EntityLinked"].apply(lambda ents: [ent.get_id() for ent in ents])
    data["Labels"] = data["EntityLinked"].apply(lambda ents: [ent.get_label() for ent in ents])
    data.head()
    # Création des listes
    # Convertir les chaînes de caractères représentant des listes en listes Python
    # Assurez-vous que les QID sont des listes d'entiers ou de chaînes avant la concaténation
    liste1_qids = data['QID'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x).tolist()
    liste1 = np.concatenate(liste1_qids)

    # Filtrer les éléments None et convertir en int
    listesansnul = [int(item) for item in liste1 if item is not None]
    UniqueList = np.unique(listesansnul)
    UniqueList2 = UniqueList.tolist()
    UniqueList3 = [f"Q{id}" if not str(id).startswith("Q") else id for id in UniqueList2]
    print(len(UniqueList3))
    return UniqueList3