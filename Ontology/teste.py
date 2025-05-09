import csv

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

pokemon_types = {
    "bug": "against_bug",
    "dark": "against_dark",
    "dragon": "against_dragon",
    "electric": "against_electric",
    "fairy": "against_fairy",
    "fighting": "against_fighting",
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

#print(gen_regions["1"])

#print(gen_regions.keys())

#for key, efectiveness in gen_regions.items():
#    print(f"{key} : {efectiveness}")

with open("./Dataset/final_pokemon.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter=",")

    for line in reader:

        for key, efectiveness in pokemon_types.items():
                switch = line[efectiveness]
                match switch:
                    case "0.0":
                        print(f"{key} : {efectiveness} : {switch}")
                    case "0.5":
                        print(f"{key} : {efectiveness} : {switch}")
                    case "1.0":
                        print(f"{key} : {efectiveness} : {switch}")
                break
        break