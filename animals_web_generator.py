import json

file_path="c:/user/marti/PycharmProject/Zootopia/animals_data.json"
def load_data(file_path):
    with open(file_path, "r") as handle:
        return json.load(handle)

animals_data = load_data("animals_data.json")


for fox in animals_data:
    #print(f"name in fox: {'name' in fox}")
    #print(f"characteristics in fox: {'characteristics' in fox}")
    #print(f"locations in fox: {'locations' in fox}")
    #for items in fox['characteristics']:
    #    print(f"type in fox[characteristics]: {'type' in items}")

    if "name" in fox:
        print(f"Name: {fox["name"]}")
    if "characteristics" in fox:
        if "diet" in fox["characteristics"]:
            print(f"Diet: {fox["characteristics"]["diet"]}")
    if "locations" in fox:
        print(f"Location: {fox["locations"][0]}")
    if "characteristics" in fox:
        if "type" in fox["characteristics"]:
            print(f"Type: {fox["characteristics"]["type"]}")
    print("======================")