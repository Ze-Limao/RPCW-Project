import requests
from rdflib import Graph
import json

CONFIG_PATH = "./app/config.json"

def clear_repository():
    config = load_config()
    # Construct the repository endpoint URL
    endpoint_url = f"{config['url']}/repositories/{config['repository_name']}/statements"

    # Send a DELETE request to clear the repository
    response = requests.delete(endpoint_url)

    # Check the response status
    if response.status_code == 204:
        print("Repository successfully cleared.")
        config["url"] = None
        config["name"] = None
        config["prefix"] = None
        
        save_config(config)
    else:
        print(f"Failed to clear repository. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r") as file:
        return json.load(file)

def save_config(config, config_path=CONFIG_PATH):
    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

def get_repository_info():
    config = load_config()

    repository_name = config['name']
    response = requests.get(f"http://localhost:7200/repositories/{repository_name}/size")
    triples_count = response.text

    result = {
        "repository_name":repository_name,
        "repository_url": config["url"],
        "prefix": config["prefix"],
        "triples_count": triples_count
    }
    return result

def get_base_prefix(ontology_file):
    graph = Graph()
    graph.parse(ontology_file, format="turtle")
    for prefix, ns in graph.namespaces():
        if prefix == "":
            return str(ns)
    return None

def update_ontology(ontology_file, repository_url, repository_name):
    config = load_config()

    config['url'] = repository_url
    config['name'] = repository_name
    config['prefix'] = get_base_prefix(ontology_file)

    save_config(config)

    load_to_graphdb(ontology_file, repository_url, repository_name)


def load_ontology_to_graphdb(ontology_file, repository_url, repository_name, base=False):
    config = load_config()

    # caso já exista um repositorio
    if config.get("url") and config.get("name") and config.get("prefix") and not base:
        print("Configuração já existente.")
        return

    # criar um novo repo
    config["url"] = repository_url

    prefix = get_base_prefix(ontology_file)
    if not prefix:
        raise ValueError("Não foi possível extrair o prefixo base da ontologia.")
    config["prefix"] = f"<{prefix}>"

    name = repository_name
    config["name"] = name

    print (f"Configuração: {config}")
    save_config(config)

    load_to_graphdb(ontology_file, repository_url, repository_name)


def load_to_graphdb(ontology_file, repository_url, repository_name):
    if not create_graphdb_repository(repository_url, repository_name):
        print("❌ Aborting load due to repo creation failure.")
        return
    
    # Load the ontology into an RDFLib graph
    graph = Graph()
    graph.parse(ontology_file, format="turtle")

    # Serialize the graph to a string in Turtle format
    ontology_data = graph.serialize(format="turtle")

    # Construct the repository endpoint URL
    endpoint_url = f"{repository_url}/repositories/{repository_name}/statements"

    # Send the ontology data to the repository
    headers = {"Content-Type": "text/turtle"}
    response = requests.post(endpoint_url, data=ontology_data, headers=headers)

    # Check the response status
    if response.status_code == 204:
        print("Ontology successfully saved to the GraphDB repository.")
    else:
        print(f"Failed to save ontology. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def create_graphdb_repository(repository_url, repository_name):
    config_ttl = f"""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix graphdb: <http://www.ontotext.com/config/graphdb#> .

[] a rep:Repository ;
   rep:repositoryID "{repository_name}" ;
   rdfs:label "{repository_name}" ;
   rep:repositoryImpl [
      rep:repositoryType "graphdb:SailRepository" ;
      sr:sailImpl [
         sail:sailType "graphdb:Sail" ;
         graphdb:ruleset "rdfsplus-optimized" ;
         graphdb:storage-folder "storage" ;
         graphdb:enable-context-index true ;
         graphdb:enablePredicateList true ;
         graphdb:enable-literal-index true ;
         graphdb:in-memory-literal-properties false ;
         graphdb:base-URL "http://example.org/ontology#" ;
         graphdb:repository-type "file-repository"
      ]
   ] .
"""

    files = {
        'config': (f'{repository_name}.ttl', config_ttl, 'text/turtle')
    }

    response = requests.post(f"{repository_url}/rest/repositories", files=files)

    if response.status_code == 201:
        print(f"✅ Repository '{repository_name}' created successfully.")
        return True
    elif response.status_code == 409:
        print(f"⚠️ Repository '{repository_name}' already exists.")
        return True
    else:
        print(f"❌ Failed to create repository. Status: {response.status_code}")
        print(response.text)
        return False
