import io
import traceback
from SPARQLWrapper import JSON, XML, CSV, TSV, SPARQLWrapper
from flask import Blueprint, request, jsonify, render_template, send_file
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
import requests
from app.queries import get_ontology_stats, get_ontology_classes, get_pokemon_by_name, get_pokemons, sparql_get_query, sparql_query
from app.ontology import clear_repository, load_ontology_to_graphdb, get_repository_info, update_ontology

main = Blueprint("main", __name__)

# deafault values
ontology_base = "./Ontology/pokemon_ontology_base.ttl"
ontology_file = "./Ontology/pokemon_povoada.ttl"
repository_url = "http://localhost:7200"
repository_name = "pokentology"

@main.route('/')
def index():
    load_ontology_to_graphdb(ontology_file, repository_url, repository_name)
    return render_template('home.html')

@main.route('/pokemon/<instance>')
def pokemon_detail(instance):
    pokemon = get_pokemon_by_name(instance)

    if pokemon:
        return render_template('pokemon.html', pokemon=pokemon), 200

@main.route('/sparql')
def sparql():
    repository_info = get_repository_info()
    return render_template('sparql.html', repository_info=repository_info)

@main.route('/generate', methods=['GET', 'POST'])
def generate_ontology():
    message = None
    error = None
    
    if request.method == 'POST':
        repo_name = request.form.get('repository_name', 'pokentology')
        try:
            load_ontology_to_graphdb(ontology_base, repository_url, repo_name, True)
            message = f"Ontology successfully generated and loaded into repository '{repo_name}'"
        except Exception as e:
            error = f"Ontology generation failed: {str(e)}"
    
    repository_info = get_repository_info()
    return render_template('generate.html', 
                          repository_info=repository_info,
                          message=message,
                          error=error)


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

@main.route('/api/sparql', methods=['POST'])
def execute_sparql():
    """Execute SELECT queries using sparql_get_query function"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Log the query for debugging
        print(f"Executing SELECT query: {query[:100]}...")
        
        try:
            # Use the existing sparql_get_query function
            results = sparql_get_query(query)
            return jsonify(results)
            
        except Exception as e:
            print(f"SPARQL query error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Error executing query: {str(e)}"}), 400
            
    except Exception as e:
        print(f"API error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@main.route('/api/sparql-update', methods=['POST'])
def execute_sparql_update():
    """Execute INSERT/UPDATE/DELETE queries using sparql_query function"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Log the query for debugging
        print(f"Executing UPDATE query: {query[:100]}...")
        
        try:
            # Use the existing sparql_query function for updates
            result = sparql_query(query)
            
            # Update operations typically don't return data, just success
            return jsonify({
                "success": True,
                "message": "Update operation completed successfully"
            })
            
        except Exception as e:
            print(f"SPARQL update error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Error executing update: {str(e)}"}), 400
            
    except Exception as e:
        print(f"API error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@main.route('/api/upload-ontology', methods=['POST'])
def upload_ontology():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    repo_name = request.form.get('repository_name', 'pokentology')
    
    try:
        # Determine content type based on file extension
        content_type = "text/turtle"  # Default to Turtle
        if file.filename.endswith('.rdf') or file.filename.endswith('.xml'):
            content_type = "application/rdf+xml"
        elif file.filename.endswith('.jsonld'):
            content_type = "application/ld+json"
        elif file.filename.endswith('.nt'):
            content_type = "application/n-triples"
        
        # Upload to GraphDB
        response = requests.post(
            f"{repository_url}/repositories/{repo_name}/statements",
            headers={"Content-Type": content_type},
            data=file.read()
        )
        
        if response.status_code == 204:
            update_ontology(ontology_file, repository_url, repo_name)
            return jsonify({"success": True, "message": "Ontology uploaded successfully"})
        else:
            return jsonify({"error": f"Upload failed: {response.text}"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@main.route('/api/download-ontology', methods=['GET'])
def download_ontology():
    repo_name = request.args.get('repository_name', 'pokentology')

    content_type ='text/turtle'
    
    try:
        # Query all triples
        response = requests.get(
            f"{repository_url}/repositories/{repo_name}/statements",
            headers={"Accept": content_type}
        )
        
        if response.status_code == 200:
            # Create a file-like object from the response content
            file_data = io.BytesIO(response.content)
            
            extension = 'ttl'
            
            return send_file(
                file_data,
                mimetype=content_type,
                as_attachment=True,
                download_name=f"{repo_name}.{extension}"
            )
        else:
            return jsonify({"error": f"Download failed: {response.text}"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@main.route('/api/delete-ontology', methods=['POST'])
def delete_ontology():
    repo_name = request.form.get('repository_name', 'pokentology')
    
    try:
        # Delete all statements in the repository
        response = requests.delete(
            f"{repository_url}/repositories/{repo_name}/statements"
        )
        
        if response.status_code == 204:
            clear_repository()
            return jsonify({"success": True, "message": "Ontology deleted successfully"})
        else:
            return jsonify({"error": f"Deletion failed: {response.text}"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500
