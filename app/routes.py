from flask import Blueprint, request, jsonify, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
# from queries
# from ontology

main = Blueprint("main", __name__)


@main.route('/')
def index():
    return render_template('home.html')

@main.route('/pokemon/<pokemon_id>')
def pokemon_detail(pokemon_id):
    # In the real app API request to get the pokemon data
    pokemon = {
        "name": "squirtle",
        "id": "0007",
        "type": "water",
        "hp": 50,
        "attack": 20,
        "defense": 15,
        "special_attack": 25,
        "special_defense": 25,
        "speed": 20,
        "height": 0.6,
        "weight": 9.0,
        "icon": "https://img.pokemondb.net/sprites/home/normal/squirtle.png",
    }
    return render_template('pokemon.html', pokemon=pokemon)

@main.route('/sparql')
def sparql():
    return render_template('sparql.html')

@main.route('/generate')
def generate_ontology():
    return render_template('generate.html')

@main.route('/explore')
def explore():
    # Sample data for the explore page
    pokemon_list = [
        {
            "name": "bulbasaur",
            "id": "0001",
            "type": "grass",
            "icon": "https://img.pokemondb.net/sprites/home/normal/bulbasaur.png",
        },
        {
            "name": "charmander",
            "id": "0004",
            "type": "fire",
            "icon": "https://img.pokemondb.net/sprites/home/normal/charmander.png",
        },
        {
            "name": "squirtle",
            "id": "0007",
            "type": "water",
            "icon": "https://img.pokemondb.net/sprites/home/normal/squirtle.png",
        },
        {
            "name": "pikachu",
            "id": "0025",
            "type": "electric",
            "icon": "https://img.pokemondb.net/sprites/home/normal/pikachu.png",
        }
    ]
    
    # Sample ontology data - in a real application, this would come from SPARQL queries
    ontology_stats = {
        "total_triples": 12458,
        "total_classes": 24,
        "total_instances": 898,
        "total_properties": 156
    }
    
    # Sample classes and their instances
    ontology_classes = [
        {
            "name": "Pokemon",
            "uri": "http://pokentology.org/ontology/Pokemon",
            "instance_count": 898,
            "instances": [
                {"name": "Bulbasaur", "uri": "http://pokentology.org/resource/Bulbasaur"},
                {"name": "Charmander", "uri": "http://pokentology.org/resource/Charmander"},
                {"name": "Squirtle", "uri": "http://pokentology.org/resource/Squirtle"}
            ]
        },
        {
            "name": "Type",
            "uri": "http://pokentology.org/ontology/Type",
            "instance_count": 18,
            "instances": [
                {"name": "Water", "uri": "http://pokentology.org/resource/WaterType"},
                {"name": "Fire", "uri": "http://pokentology.org/resource/FireType"},
                {"name": "Grass", "uri": "http://pokentology.org/resource/GrassType"}
            ]
        },
        {
            "name": "Ability",
            "uri": "http://pokentology.org/ontology/Ability",
            "instance_count": 267,
            "instances": [
                {"name": "Overgrow", "uri": "http://pokentology.org/resource/Overgrow"},
                {"name": "Blaze", "uri": "http://pokentology.org/resource/Blaze"},
                {"name": "Torrent", "uri": "http://pokentology.org/resource/Torrent"}
            ]
        },
        {
            "name": "Move",
            "uri": "http://pokentology.org/ontology/Move",
            "instance_count": 826,
            "instances": [
                {"name": "Tackle", "uri": "http://pokentology.org/resource/Tackle"},
                {"name": "Ember", "uri": "http://pokentology.org/resource/Ember"},
                {"name": "Water Gun", "uri": "http://pokentology.org/resource/WaterGun"}
            ]
        },
        {
            "name": "Generation",
            "uri": "http://pokentology.org/ontology/Generation",
            "instance_count": 8,
            "instances": [
                {"name": "Generation I", "uri": "http://pokentology.org/resource/Generation1"},
                {"name": "Generation II", "uri": "http://pokentology.org/resource/Generation2"},
                {"name": "Generation III", "uri": "http://pokentology.org/resource/Generation3"}
            ]
        }
    ]
    
    return render_template('explore.html', 
                          pokemon_list=pokemon_list, 
                          ontology_stats=ontology_stats,
                          ontology_classes=ontology_classes)


def sparql_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/advogados/statements")
    sparql.setMethod('POST')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def sparql_get_query(query):
    sparql = SPARQLWrapper("http://localhost:7200/repositories/advogados")
    sparql.setMethod('GET')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()



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
    
    # In a real application, you would execute these queries and return the results
    # For now, we'll return sample data
    return {
        "total_triples": 12458,
        "total_classes": 24,
        "total_instances": 898,
        "total_properties": 156
    }

# Function to get classes and their instances (would be used in a real application)
def get_ontology_classes():
    # Query to get all classes and count their instances
    classes_query = """
    SELECT ?class ?className (COUNT(DISTINCT ?instance) AS ?instanceCount)
    WHERE {
        ?class a <http://www.w3.org/2002/07/owl#Class> .
        OPTIONAL {
            ?instance a ?class
        }
        BIND(STRAFTER(STR(?class), "#") AS ?className)
    }
    GROUP BY ?class ?className
    ORDER BY DESC(?instanceCount)
    """
    
    # Query to get instances for a specific class
    instances_query = """
    SELECT ?instance ?instanceName
    WHERE {
        ?instance a <{class_uri}> .
        BIND(STRAFTER(STR(?instance), "#") AS ?instanceName)
    }
    LIMIT 10
    """
    
    # In a real application, you would execute these queries and return the results
    # For now, we'll return sample data
    return [
        {
            "name": "Pokemon",
            "uri": "http://pokentology.org/ontology/Pokemon",
            "instance_count": 898,
            "instances": [
                {"name": "Bulbasaur", "uri": "http://pokentology.org/resource/Bulbasaur"},
                {"name": "Charmander", "uri": "http://pokentology.org/resource/Charmander"},
                {"name": "Squirtle", "uri": "http://pokentology.org/resource/Squirtle"}
            ]
        },
        # Other classes would be here
    ]
