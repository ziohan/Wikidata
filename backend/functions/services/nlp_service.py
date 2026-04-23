import spacy

def load_nlp():
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe("entityLinker", last=True)
    return nlp

# singleton (carrega uma vez só)
nlp = load_nlp()