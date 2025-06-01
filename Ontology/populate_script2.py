from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
import requests
import json
import os
import csv

endpoint_moves = "https://pokeapi.co/api/v2/move?limit=10000"

g = Graph()
g.parse("pokemon_new_povoada2.ttl", format="turtle")

n = Namespace("http://www.semanticweb.org/gonca/ontologies/2025/pokemon_ontology#")

movesset = set()

g.add((n.Moves, RDF.type, OWL.Class))


g.add((n.learnedby, RDF.type, OWL.ObjectProperty))
g.add((n.learnedby, RDFS.domain, n.Moves))
g.add((n.learnedby, RDFS.range, n.Pokemon))

g.add((n.fromType, RDF.type, OWL.ObjectProperty))
g.add((n.fromType, RDFS.domain, n.Moves))
g.add((n.fromType, RDFS.range, n.Type))

g.add((n.accuracy, RDF.type, OWL.DatatypeProperty))
g.add((n.accuracy, RDFS.range, XSD.integer))

g.add((n.damageClass, RDF.type, OWL.DatatypeProperty))
g.add((n.damageClass, RDFS.range, XSD.string))

g.add((n.power, RDF.type, OWL.DatatypeProperty))
g.add((n.power, RDFS.range, XSD.integer))

g.add((n.pp, RDF.type, OWL.DatatypeProperty))
g.add((n.pp, RDFS.range, XSD.integer))

g.add((n.priority, RDF.type, OWL.DatatypeProperty))
g.add((n.priority, RDFS.range, XSD.integer))

g.add((n.moveID, RDF.type, OWL.DatatypeProperty))
g.add((n.moveID, RDFS.range, XSD.integer))

g.add((n.effectChance, RDF.type, OWL.DatatypeProperty))
g.add((n.effectChance, RDFS.range, XSD.string))

g.add((n.effect, RDF.type, OWL.DatatypeProperty))
g.add((n.effect, RDFS.range, XSD.string))


response_moves = requests.get(endpoint_moves)

if response_moves.status_code != 200:
    print("Error fetching moves data from PokeAPI")
else:
    for move in response_moves.json()['results']:
        move_name = move['name'].replace(" ", "_")
        move_name = move_name.replace("-", "_")
        move_uri = URIRef(f"{n}{move_name}")
        print(f"Processing move: {move_name}")
        if move_uri not in movesset:
            g.add((move_uri, RDF.type, OWL.NamedIndividual))
            g.add((move_uri, RDF.type, n.Moves))
            g.add((move_uri, n.name, Literal(move_name)))
            response_move_details = requests.get(move['url'])
            if response_move_details.status_code != 200:
                print(f"Error fetching details for move {move_name}")
                continue
            else:
                move_details = response_move_details.json()
                print(f"Adding details for move: {move_name}")
                accuracy = move_details["accuracy"]
                g.add((move_uri, n.accuracy, Literal(accuracy, datatype=XSD.integer)))
                damage_class = move_details["damage_class"]["name"]
                g.add((move_uri, n.damageClass, Literal(damage_class, datatype=XSD.string))) #podia ser uma subclasse dos moves
                effect_chance = move_details["effect_chance"]
                if effect_chance:
                    g.add((move_uri, n.effectChance, Literal(effect_chance, datatype=XSD.string)))
                else:
                    g.add((move_uri, n.effectChance, Literal("There is no effect", datatype=XSD.string)))
                for effect in move_details["effect_entries"]:
                    if effect["language"]["name"] == "en":
                        effect_str = effect["effect"]
                        g.add((move_uri, n.effect, Literal(effect_str, datatype=XSD.string)))
                move_id = move_details["id"]
                g.add((move_uri, n.moveID, Literal(move_id, datatype=XSD.integer)))
                power = move_details["power"]
                g.add((move_uri, n.power, Literal(power, datatype=XSD.integer)))
                pp = move_details["pp"]
                g.add((move_uri, n.pp, Literal(pp, datatype=XSD.integer)))
                priority = move_details["priority"]
                g.add((move_uri, n.priority, Literal(priority, datatype=XSD.integer))) ## podia ser bool
                for pokemon in move_details["learned_by_pokemon"]:
                    pokemon_name = pokemon["name"].replace(" ", "_")
                    pokemon_uri = URIRef(f"{n}{pokemon_name}")
                    g.add((move_uri, n.learnedby, pokemon_uri))
                    
                type = move_details["type"]["name"].replace(" ", "_")
                type_uri = URIRef(f"{n}{type}")
                g.add((move_uri, n.fromType, type_uri))
                print(f"id : {move_id}")

            movesset.add(move_uri)

g.serialize(destination="pokemon_new_povoada_withmoves.ttl", format="turtle")
print(len(g))

                