from SPARQLWrapper import SPARQLWrapper, JSON

prefix = "<http://www.semanticweb.org/gonca/ontologies/2025/pokemon_ontology#>"
clean_prefix = prefix.strip("<>")

def get_pokemon_by_name(instance):
    instance_uri = clean_prefix + instance 
    query = f"""
    SELECT ?property ?value
    WHERE {{
      <{instance_uri}> ?property ?value .
    }}
    """

    result = sparql_get_query(query)

    pokemon = {
        "relations": {}
    }

    if result['results']['bindings']:
        for linha in result['results']['bindings']:
            property_uri = linha['property']['value']
            property_name = property_uri.split("#")[-1] if "#" in property_uri else property_uri.split("/")[-1]
            value = linha['value']['value']
            is_literal = linha['value']['type'] == "literal"

            clean_value = value.split("#")[-1] if "#" in value else value.split("/")[-1]

            if is_literal:
                pokemon[property_name] = clean_value
            else:
                if property_name not in pokemon["relations"]:
                    pokemon["relations"][property_name] = []
                pokemon["relations"][property_name].append(clean_value)

    return pokemon

def get_pokemons():
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
    return pokemon_list

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