# 📖 Knowledge Graph Generator
### Creation of an application for generating Wikidata triplets for entities

## 📌 Project Overview

This project was developed as part of a university project.  

The goal was to build an **application capable of extracting triplets from the Wikipedia API and generating a graph visualization and a text file with this information**

The main challenge was **information ranking**: training a model capable of getting the triplets and ranking them based on the provided title

---

## 🎲 Data Source and Tools

- **DBLP1_processed_.csv dataset**  
  Contains 3065 query examples with title, entities ids and entities labels

- **Wikidata**  
  Wikipedia's API which allows access to Wikipedia's dataset

- **SPARQL**  
  Queries Wikidata with subject-predicate-object queries

---

## ⚙️  Data Processing Pipeline

Using techniques such as **data cleaning, data linking, and feature engineering**, a complete pipeline was designed that is capable of:

---

### Dataset Preprocessing

- Data importation from CSV file

- Entity linking to obtain IDs

- Filtering of unvalid triplets

- QIDs convertion to standard Wikidata format

---

### Data Enrichment

- Triplet Extraction by labels extraction from ids

- Entities, predicates, and triples insertion into the database

- Extraction of new data from Wikipedia if not in database

---

### 🤖 Training Model

---

Using methods such as **data embedding** and **data bi-encoding**, a hybrid model using **tranformers**, **weighting predicate** and **cosine similarity** was developed, using:

- Triplet Cosine similarity: Similarity of embeddings between title and triplet using cosines and bi-encoding

<p align = "center">
<strong><code>Cosine_Score = cos(title, triplet)</code></strong>
</p>

- Entity Cosine Similarity: Applies cosine similarity between title and entities and gets the maximum of them

<p align = "center">
<strong><code>Entity_Score = max(cos(title, subject), cos(title, object))</code></strong>
</p>

<p align="center">
<img width="480" height = "270" height="342" alt="cosine_similarity" src="https://github.com/user-attachments/assets/c3e6245a-7e92-473c-9dec-c218ac2fb316" />
</p>

- Cross-encoder: Analyzes the relationship between title and triplet using a shared encoder and transformers

<p align="center">
<img width="480" height="270" alt="Bi_vs_Cross-Encoder" src="https://github.com/user-attachments/assets/869d9d0d-ea9e-4e8f-8079-73597982a2eb" />
</p>

- Weight Predicate: Applies a weight for some predicates, filtering manualy which ones are more relevant to the project context 

<p align = "center">
<strong><code>score = base x (0.75 + 0.25 x predicate_weight)</code></strong>
</p>

Which the base value is obtained with the following formula:

<p align = "center">
<strong><code>base = 0.45 x triplet_score + 0.35 x cross_score + 0.2 entity_score</code></strong>
</p>

---

### 📈 Graph Generation Model

---

<p align = "center">
<img width="480" height="270" alt="Graph_Example" src="https://github.com/user-attachments/assets/21100ee5-bf9d-467e-8fe6-6dff7a0b2a5f" />
</p>

## 📊 Model Evaluation

As there were no dataset labels containing the necessary data to say if the triplet was correct or not for the query, there was no evaluation method implemented on the project. However, a series of tests were executed, obtaining consistent information as output, as it can be seen below with the input ``"What is the capital of France?"`` and the best scored output being ``"France capital Paris"``

<img width="1100" height="500" alt="query data" src="https://github.com/user-attachments/assets/f8166dbd-4d1b-421c-ae9b-7f495e0a83b8" />

## 🧰 Tools and Libraries Used
- ``Wikidata`` - Wikipedia API which allows access to Wikipedia's dataset
- ``SPARQL`` - Queries Wikidata with subject-predicate-object queries
- `Angular` – Frontend development
- `FastAPI` – Database manipulation
- `numpy` – Mathematical operations
- `SpaCy` – NLP manipulation
- `scikit-learn` – Model training, evaluation, and metrics
- `Sentence Transformers` – Bi-encoding and Cross-encoding models importation

## 🚀 Future Improvements
Potential next steps for this project include:

- Project optimization for larger data volumes

- Testing of different versions of models

- Integration of new techniques of structuring data using Docling and SpaCy for Named Entity Recognition (NER) implementation

## 🔗 Final Notes
This project highlights how NLP combined with embeddings and transformers methods can be used to enrich entities context by triplets extraction from Wikidata using SPARQL.

📌 I invite you to explore the full repository and dive deeper into the implementation.
