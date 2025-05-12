import requests
from rdflib import Graph

def clear_repository(repository_url, repository_name):
    # Construct the repository endpoint URL
    endpoint_url = f"{repository_url}/repositories/{repository_name}/statements"

    # Send a DELETE request to clear the repository
    response = requests.delete(endpoint_url)

    # Check the response status
    if response.status_code == 204:
        print("Repository successfully cleared.")
    else:
        print(f"Failed to clear repository. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def save_ontology_to_graphdb(ontology_file, repository_url, repository_name):
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
