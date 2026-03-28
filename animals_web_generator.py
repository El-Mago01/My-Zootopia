import json

file_path="c:/user/marti/PycharmProject/Zootopia/animals_data.json"

def load_animals_data(file_path):
    with open(file_path, "r") as handle:
        return json.load(handle)

def load_html_file(file_path):
    with open(file_path, "r") as handle:
        return handle.read()

def write_to_new_html_file(content):
    with open("animals.html", "w") as f:
        f.write(content)

def main():
    animals_data = load_animals_data("animals_data.json")
    html_data=load_html_file("animals_template.html")
    __replace__= "__REPLACE_ANIMALS_INFO__"
    animal_repository_string=""

    for fox in animals_data:
        animal_repository_string+='<li class="cards__item">\n'
        if "name" in fox:
            animal_repository_string+=f"Name: {fox['name']}<br/>\n"
        if "characteristics" in fox:
            if "diet" in fox["characteristics"]:
                animal_repository_string += f"Diet: {fox["characteristics"]["diet"]}<br/>\n"
        if "locations" in fox:
            animal_repository_string += f"Location: {fox["locations"][0]}<br/>\n"
        if "characteristics" in fox:
            if "type" in fox["characteristics"]:
                animal_repository_string += f"Type: {fox["characteristics"]["type"]}<br/>\n"
        animal_repository_string+='</li>\n'
    # The replacement below is necessary to avoid a mojibake
    animal_repository_string=animal_repository_string.replace("â€™","\'")
    #print(animal_repository_string)
    # Replace the string to replace in the html with the animal repository
    html_data=html_data.replace(__replace__,animal_repository_string)

    write_to_new_html_file(html_data)
    #print(html_data)

if __name__ == "__main__":
    main()