from flask import Blueprint, request, jsonify, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
# from queries
# from ontology

main = Blueprint("main", __name__)

prefix = "<http://www.semanticweb.org/gonca/ontologies/2025/pokemon_ontology#>"

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/pokemon/<pokedex_number>')
def pokemon_detail(pokedex_number):
    # SPARQL query to get all properties of the Pokémon
    query = f"""
    PREFIX : {prefix}
    SELECT ?property ?value
    WHERE {{
        ?pokemon a :Pokemon ;
            :pokedex_number {pokedex_number} ;
            ?property ?value .
    }}
    """
    result = sparql_get_query(query)

    if result['results']['bindings']:
        linhas = result['results']['bindings']
        pokemon = {}
        for linha in linhas:
            property_name = linha['property']['value'].split("#")[-1]
            if property_name == "hasType":
                if "hasType" not in pokemon:
                    pokemon["hasType"] = []
                pokemon["hasType"].append(linha['value']['value'].split("#")[-1])
            else:
                pokemon[property_name] = linha['value']['value'].split("#")[-1]
        return render_template('pokemon.html', pokemon=pokemon), 200
    else:
        return render_template('pokemon-not-found.html'), 404

@main.route('/sparql')
def sparql():
    return render_template('sparql.html')

@main.route('/generate')
def generate_ontology():
    return render_template('generate.html')

@main.route('/explore')
def explore():
    # SPARQL query to get name and pokedex number for all Pokémon instances
    query_pokemon = f"""
    PREFIX : {prefix}
    SELECT ?name ?pokedex_number
    WHERE {{
        ?pokemon a :Pokemon ;
            :name ?name ;
            :pokedex_number ?pokedex_number .
    }} ORDER BY ?pokedex_number
    """

    result = sparql_get_query(query_pokemon)
    pokemon_list = []
    for row in result['results']['bindings']:
        pokemon = {
            "name": row['name']['value'],
            "pokedex_number": row['pokedex_number']['value']
        }
        pokemon_list.append(pokemon)

    ontology_stats = get_ontology_stats()
    ontology_classes = get_ontology_classes()

    # Format the classes data for the template
    formatted_classes = {}
    for class_name, instances in ontology_classes.items():
        formatted_classes[class_name] = instances

    return render_template('explore.html', 
                          pokemon_list=pokemon_list, 
                          stats=ontology_stats,
                          classes=formatted_classes)

@main.route('/api/class-instances/<class_name>')
def get_class_instances(class_name):
    """API endpoint to get instances of a specific class"""
    query = f"""
    PREFIX : {prefix}
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?instance
    WHERE {{
        ?instance a :{class_name} .
    }}
    ORDER BY ?instance
    """
    
    result = sparql_get_query(query)
    instances = []
    
    for row in result['results']['bindings']:
        instance_uri = row['instance']['value']
        instance_name = instance_uri.split('#')[-1]
        instances.append(instance_name)
    
    return jsonify(instances)

def get_ontology_stats():
    # Query to count total triples
    total_triples_query = """
    SELECT (COUNT(*) AS ?count) 
    WHERE { ?s ?p ?o }
    """
    
    # Query to count classes
    classes_query = """
    SELECT (COUNT(DISTINCT ?class) AS ?count) 
    WHERE { 
        ?class a <http://www.w3.org/2002/07/owl#Class> 
    }
    """
    
    # Query to count instances
    instances_query = """
    SELECT (COUNT(DISTINCT ?instance) AS ?count) 
    WHERE { 
        ?instance a ?class .
        ?class a <http://www.w3.org/2002/07/owl#Class> 
    }
    """
    
    # Query to count properties
    properties_query = """
    SELECT (COUNT(DISTINCT ?property) AS ?count) 
    WHERE { 
        { ?property a <http://www.w3.org/2002/07/owl#ObjectProperty> }
        UNION
        { ?property a <http://www.w3.org/2002/07/owl#DatatypeProperty> }
    }
    """
    
    # Execute the queries
    triples = sparql_get_query(total_triples_query)['results']['bindings'][0]['count']['value']
    classes = sparql_get_query(classes_query)['results']['bindings'][0]['count']['value']
    instances = sparql_get_query(instances_query)['results']['bindings'][0]['count']['value']
    properties = sparql_get_query(properties_query)['results']['bindings'][0]['count']['value']
    
    return {
        "triples": triples,
        "classes": classes,
        "instances": instances,
        "properties": properties
    }

def get_ontology_classes():
    query = """
    SELECT DISTINCT ?class ?instance
    WHERE {
        ?instance a ?class .
        ?class a <http://www.w3.org/2002/07/owl#Class> .
    }
    ORDER BY ?class
    """

    result = sparql_get_query(query)
    class_dict = {}

    for row in result['results']['bindings']:
        class_name = row['class']['value'].split("#")[-1]
        instance_name = row['instance']['value'].split("#")[-1]

        if class_name not in class_dict:
            class_dict[class_name] = []

        class_dict[class_name].append(instance_name)

    return class_dict


def sparql_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pokentology/statements")
    sparql.setMethod('POST')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def sparql_get_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/pokentology")
    sparql.setMethod('GET')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
