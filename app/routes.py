import traceback
from SPARQLWrapper import JSON, XML, CSV, TSV, SPARQLWrapper
from flask import Blueprint, request, jsonify, render_template
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from app.queries import get_ontology_stats, get_ontology_classes, get_pokemon_by_name, get_pokemons
from app.ontology import clear_repository, save_ontology_to_graphdb

main = Blueprint("main", __name__)

ontology_file = "./Ontology/pokemon_povoada.ttl"
repository_url = "http://localhost:7200"
repository_name = "pokentology"

@main.route('/')
def index():
    save_ontology_to_graphdb(ontology_file, repository_url, repository_name)
    return render_template('home.html')

@main.route('/pokemon/<pokedex_number>')
def pokemon_detail(pokedex_number):
    pokemon = get_pokemon_by_name(pokedex_number)

    if pokemon:
        return render_template('pokemon.html', pokemon=pokemon), 200
    else:
        return render_template('pokemon-not-found.html'), 404

@main.route('/sparql')
def sparql():
    return render_template('sparql.html')

@main.route('/api/sparql', methods=['POST'])
def execute_sparql():
    try:
        data = request.json
        query = data.get('query', '')
        endpoint = data.get('endpoint', 'http://localhost:7200/repositories/pokentology')
        format_type = data.get('format', 'json')
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Set up SPARQL wrapper
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        
        # Set return format based on user selection
        if format_type == 'json':
            sparql.setReturnFormat(JSON)
        elif format_type == 'xml':
            sparql.setReturnFormat(XML)
        elif format_type == 'csv':
            sparql.setReturnFormat(CSV)
        elif format_type == 'tsv':
            sparql.setReturnFormat(TSV)
        else:
            sparql.setReturnFormat(JSON)
        
        try:
            results = sparql.query().convert()
            
            # If not JSON format, convert to JSON for the response
            if format_type != 'json':
                if format_type == 'xml':
                    return jsonify({
                        "head": {"vars": ["result"]},
                        "results": {
                            "bindings": [
                                {"result": {"type": "literal", "value": str(results)}}
                            ]
                        }
                    })
                elif format_type in ['csv', 'tsv']:
                    lines = results.decode('utf-8').strip().split('\n')
                    headers = lines[0].split(',' if format_type == 'csv' else '\t')
                    
                    bindings = []
                    for line in lines[1:]:
                        values = line.split(',' if format_type == 'csv' else '\t')
                        binding = {}
                        for i, header in enumerate(headers):
                            if i < len(values):
                                binding[header] = {"type": "literal", "value": values[i]}
                        bindings.append(binding)
                    
                    return jsonify({
                        "head": {"vars": headers},
                        "results": {"bindings": bindings}
                    })
            
            return jsonify(results)
        except Exception as e:
            # Log the error for debugging
            print(f"SPARQL query error: {str(e)}")
            print(traceback.format_exc())
            
            return jsonify({"error": f"Error executing query: {str(e)}"}), 400
            
    except Exception as e:
        # Log the error for debugging
        print(f"API error: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Generate Ontology


@main.route('/generate')
def generate_ontology():
    return render_template('generate.html')

@main.route('/explore')
def explore():
    pokemon_list = get_pokemons()

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

