import requests
import json


endpoint = "https://pokeapi.co/api/v2/item/1/"
response = requests.get(endpoint)
if response.status_code == 200:
    data = response.json()
    with open("./jsontestes/item.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Data retrieved successfully and saved to item.json")

print("Datatype of 'cost':", type(data.get("cost")).__name__)

