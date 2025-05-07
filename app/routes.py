from flask import Blueprint, request, jsonify, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
# from queries
# from ontology

main = Blueprint("main", __name__)

@main.route('/')
def index():
    pokemon = {
        "name": "squirtle",
        "type": "water",
        "hp": 50,
        "attack": 20,
        "icon": "https://img.pokemondb.net/sprites/home/normal/squirtle.png",
    }
    return render_template('home.html', pokemon=pokemon)
