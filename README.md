# Pokentology

An ontology-based system to represent the Pokémon universe.
The ontology models entities such as Pokémon, regions, moves, items, types, and their relationships, using RDF and OWL for a formal, semantic, and extensible representation.

It also includes SPARQL queries for extracting and analyzing knowledge, leveraging semantic reasoning capabilities.

## 🔨 Development

We used a local repository in GraphDB as our database, we can use this graphdb docker image:

```
docker pull khaller/graphdb-free
```

We create volume for data persistency:

```
docker volume create graphdb_data
```

Run the container:

```
docker run -d -p 7200:7200 -v graphdb_data:/opt/graphdb/home --name my_graphdb_instance <id imagem>
```


Run app:

```
python run.py
```

## 🚀 Powered By

* **Python 3.12+** – Scripts, data processing, and ontology population
* **HTML / CSS / JavaScript** – Frontend
* **Flask** – Web framework
* **RDFlib** – RDF graph manipulation and serialization
* **D3.js** – Data visualization
* **GraphDB** – Triplestore for SPARQL storage and queries
* **External APIs** – PokeAPI, Kaggle

## 📒 Features

### Home Page
<img width="1920" height="1080" alt="home" src="https://github.com/user-attachments/assets/dfa84cd6-b78b-4338-b11d-9ebf3c0f720d" />

### Explore Page
<img width="1920" height="1080" alt="explore" src="https://github.com/user-attachments/assets/e04b1cfb-c91f-49e7-a342-140aead2d850" />

### SELECT Queries
<img width="1920" height="1080" alt="sparql" src="https://github.com/user-attachments/assets/b3459ff5-efab-4e31-a427-6b77cb83a324" />

### INSERT/UPDATE/DELETE Queries
<img width="1920" height="1080" alt="sparql2" src="https://github.com/user-attachments/assets/d6842761-4ba3-44f8-8324-a303b363b1e1" />

### Entity Properties
<img width="1920" height="1080" alt="props" src="https://github.com/user-attachments/assets/cb474f34-cab6-4945-8f89-d65cc71a2391" />

### Related Entities
<img width="1920" height="1080" alt="rels" src="https://github.com/user-attachments/assets/1c6e9e1a-fb53-4d1e-a409-15cbc91a928a" />

### Ontology Management
<img width="1920" height="1080" alt="generate" src="https://github.com/user-attachments/assets/a87d540a-2e34-47d6-814b-05e0c03f5c37" />

### Graph Visualization
<img width="1919" height="1075" alt="graph" src="https://github.com/user-attachments/assets/97ddb340-317a-466c-83fa-130bd07a5880" />

## 👥 Team

* José Correia
* Gonçalo Costa
