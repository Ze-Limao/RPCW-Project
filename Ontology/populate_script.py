from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
import requests
import json
import os
import csv

endpoint_item_category = "https://pokeapi.co/api/v2/item-category/?limit=60"

endpoint_items = "https://pokeapi.co/api/v2/item?limit=2167"



g = Graph()
g.parse("pokemon_ontology_base.ttl", format="turtle")

n = Namespace("http://www.semanticweb.org/gonca/ontologies/2025/pokemon_ontology#")

pokemonset = set()
abilitiesset = set()
regionsset = set()
typeset = set()
itemsset = set()
atributeitemset = set()

pokemon_types = {
    "bug": "against_bug",
    "dark": "against_dark",
    "dragon": "against_dragon",
    "electric": "against_electric",
    "fairy": "against_fairy",
    "fighting": "against_fight",
    "fire": "against_fire",
    "flying": "against_flying",
    "ghost": "against_ghost",
    "grass": "against_grass",
    "ground": "against_ground",
    "ice": "against_ice",
    "normal": "against_normal",
    "poison": "against_poison",
    "psychic": "against_psychic",
    "rock": "against_rock",
    "steel": "against_steel",
    "water": "against_water",
}

gen_regions = {
    "1" : "Kanto",
    "2" : "Johto",
    "3" : "Hoenn",
    "4" : "Sinnoh",
    "5" : "Unova",
    "6" : "Kalos",
    "7" : "Alola",
    "8" : "Galar",
    "9" : "Paldea",
}

###############################################################################
################### First populate with the initial csv########################
###############################################################################

with open("./Dataset/final_pokemon.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter=",")
    
    #povate types
    for type_name in pokemon_types.keys():
        typeURI = URIRef(f"{n}{type_name.replace(' ', '_')}")
        if typeURI not in typeset:
            g.add((typeURI, RDF.type, OWL.NamedIndividual))
            g.add((typeURI, RDF.type, n.Type))
            g.add((typeURI, n.name, Literal(type_name)))
            typeset.add(typeURI)

    #povate regions
    for region_name in gen_regions.values():
        regionURI = URIRef(f"{n}{region_name}")
        if regionURI not in regionsset:
            g.add((regionURI, RDF.type, OWL.NamedIndividual))
            g.add((regionURI, RDF.type, n.Region))
            g.add((regionURI, n.name, Literal(region_name)))
            regionsset.add(regionURI)

    #povoate pokemons
    for line in reader:
        pokemonURI = URIRef(f"{n}{line["name"].replace(" ", "_")}")
        if pokemonURI not in pokemonset:
            g.add((pokemonURI, RDF.type, OWL.NamedIndividual))

        switch = line["is_legendary"]
        match switch:
            case "0":
                g.add((pokemonURI, RDF.type, n.PokemonNormal))
            case "1":
                g.add((pokemonURI, RDF.type, n.PokemonLegendary))
            case "0.5":
                g.add((pokemonURI, RDF.type, n.PokemonPseudoLegendary))
        
        pokemonset.add(pokemonURI)

        #add evolution of that pokemon
        if line["Evolution"]:
            pokemonEvolutionURI = URIRef(f"{n}{line["Evolution"].replace(" ", "_")}")
            if pokemonEvolutionURI not in pokemonset:
                g.add((pokemonEvolutionURI, RDF.type, OWL.NamedIndividual))
                
            g.add((pokemonURI, n.EvolvesTo, pokemonEvolutionURI))
            g.add((pokemonEvolutionURI, n.evolvesFrom, pokemonURI))

        #add types
        if line["type1"]:
            g.add((pokemonURI, n.hasType, URIRef(f"{n}{line["type1"].replace(" ", "_")}")))
        if line["type2"]:
            g.add((pokemonURI, n.hasType, URIRef(f"{n}{line["type2"].replace(" ", "_")}")))

        #add region
        g.add((pokemonURI, n.isFrom, URIRef(f"{n}{gen_regions[line["generation"]]}" )))

        #add data properties
        g.add((pokemonURI, n.name, Literal(line["name"])))
        g.add((pokemonURI, n.base_attack, Literal(int(line["attack"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_egg_steps, Literal(int(line["base_egg_steps"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_happiness, Literal(int(line["base_happiness"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_total, Literal(int(line["base_total"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.catch_rate, Literal(line["capture_rate"], datatype=XSD.string)))
        g.add((pokemonURI, n.poke_class, Literal(line["classfication"], datatype=XSD.string)))
        g.add((pokemonURI, n.base_defense, Literal(int(line["defense"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.experience_needed, Literal(int(line["experience_growth"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.height, Literal(line["height_m"], datatype=XSD.string)))
        g.add((pokemonURI, n.base_hp, Literal(int(line["hp"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.jpn_name, Literal(line["japanese_name"], datatype=XSD.string)))
        if line["percentage_male"]:
            g.add((pokemonURI, n.male_percentage, Literal(float(line["percentage_male"]), datatype=XSD.float)))
        else:
            g.add((pokemonURI, n.male_percentage, Literal(100.0, datatype=XSD.float)))
        g.add((pokemonURI, n.pokedex_number, Literal(int(line["pokedex_number"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_special_attack, Literal(int(line["sp_attack"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_special_defense, Literal(int(line["sp_defense"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.base_speed, Literal(int(line["speed"]), datatype=XSD.integer)))
        g.add((pokemonURI, n.weight, Literal(line["weight_kg"], datatype=XSD.string)))

        #add types effectiveness
        for key, efectiveness in pokemon_types.items():
            switch = line[efectiveness]
            match switch:
                case "0.0":
                    g.add((pokemonURI, n.isResistant, URIRef(f"{n}{key.replace(' ', '_')}")))
                case "0.25":
                    g.add((pokemonURI, n.takes025xDamage, URIRef(f"{n}{key.replace(' ', '_')}")))
                case "0.5":
                    g.add((pokemonURI, n.takes05xDamage, URIRef(f"{n}{key.replace(' ', '_')}")))
                case "1.0":
                    g.add((pokemonURI, n.normalDamage, URIRef(f"{n}{key.replace(' ', '_')}")))
                case "2.0":
                    g.add((pokemonURI, n.takes2xDamage, URIRef(f"{n}{key.replace(' ', '_')}")))
                case "4.0":
                    g.add((pokemonURI, n.takes4xDamage, URIRef(f"{n}{key.replace(' ', '_')}")))

        #add abilities
        exec(f'line["abilities"] = {line["abilities"]}')
        for ability in line["abilities"]:
            abilityURI = URIRef(f"{n}{ability.replace(' ', '_')}")
            if abilityURI not in abilitiesset:
                g.add((abilityURI, RDF.type, OWL.NamedIndividual))
                g.add((abilityURI, RDF.type, n.Ability))
                g.add((abilityURI, n.name, Literal(ability)))
                abilitiesset.add(abilityURI)
            g.add((pokemonURI, n.hasAbility, abilityURI))


###############################################################################
################### Itens with the pokeapi ####################################
###############################################################################

g.add((n.items, RDF.type, OWL.Class))

g.add((n.ItemAttributes, RDF.type, OWL.Class))

g.add((n.hasAtribute, RDF.type, OWL.ObjectProperty))
g.add((n.hasAtribute, RDFS.domain, n.items))
g.add((n.hasAtribute, RDFS.range, n.ItemAttributes))

g.add((n.cost, RDF.type, OWL.DatatypeProperty))
g.add((n.cost, RDFS.range, XSD.integer))

g.add((n.effect, RDF.type, OWL.DatatypeProperty))
g.add((n.effect, RDFS.range, XSD.string))

g.add((n.itemID, RDF.type, OWL.DatatypeProperty))
g.add((n.itemID, RDFS.range, XSD.integer))



response = requests.get(endpoint_item_category)
if response.status_code != 200:
    print(f"Error fetching item categories: {response.status_code} - {response.text}")
else:
    for item_category in response.json()["results"]:
        item_category_name = item_category["name"].replace(" ", "_")
        item_category_name = item_category_name.replace("-", "_")
        item_category_uri = URIRef(f"{n}{item_category_name}")
        g.add((item_category_uri, RDF.type, OWL.Class))
        g.add((item_category_uri, RDFS.subClassOf, n.items))

##
response_item = requests.get(endpoint_items)
if response_item.status_code != 200:
    print(f"Error fetching items: {response_item.status_code} - {response_item.text}")
else:
    for item in response_item.json()["results"]:
        print(f"Processing item: {item['name']}")
        item_name = item["name"].replace(" ", "_")
        item_name = item_name.replace("-", "_")
        item_uri = URIRef(f"{n}{item_name}")
        if item_uri not in itemsset:
            g.add((item_uri, RDF.type, OWL.NamedIndividual))
            g.add((item_uri, n.name, Literal(item_name)))
            response_item_details = requests.get(item["url"])
            if response_item_details.status_code != 200:
                print(f"Error fetching item details: {response_item_details.status_code} - {response_item_details.text}")
                continue
            else:
                item_details = response_item_details.json()
                print(f"Item details for: {item_name}")
                for item_atribute in item_details["attributes"]:
                    item_attribute_name = item_atribute["name"].replace(" ", "_")
                    item_attribute_name = item_attribute_name.replace("-", "_")
                    if item_attribute_name not in atributeitemset:
                        item_attribute_uri = URIRef(f"{n}{item_attribute_name}")
                        g.add((item_attribute_uri, RDF.type, OWL.NamedIndividual))
                        g.add((item_attribute_uri, RDF.type, n.ItemAttributes))
                        g.add((item_attribute_uri, n.name, Literal(item_attribute_name)))
                        atributeitemset.add(item_attribute_uri)
                    g.add((item_uri, n.hasAtribute, item_attribute_uri))

                item_category = item_details["category"]
                item_category_name2 = item_category["name"].replace(" ", "_")
                item_category_name2 = item_category_name2.replace("-", "_")
                item_category_uri2 = URIRef(f"{n}{item_category_name2}")
                g.add((item_uri, RDF.type, item_category_uri2))
                
                print(f"Item category")

                item_cost = item_details.get("cost", 0)
                g.add((item_uri, n.cost, Literal(item_cost, datatype=XSD.integer)))
                print(f"Item cost")

                for item_effect in item_details["effect_entries"]:
                    if item_effect["language"]["name"] == "en":
                        effect = item_effect["effect"]
                        g.add((item_uri, n.effect, Literal(effect, datatype=XSD.string)))
                print(f"Item effect")

                item_id = item_details.get("id", 0)
                g.add((item_uri, n.itemID, Literal(item_id, datatype=XSD.integer)))
                print(f"Item ID: {item_id}")
            itemsset.add(item_uri)



g.serialize(destination="pokemon_new_povoada2.ttl", format="turtle")
print(len(g))
                

            
        
