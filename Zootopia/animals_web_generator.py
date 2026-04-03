import json

file_path="c:/user/marti/PycharmProject/Codio/animals_data.json"

def load_animals_data(file_path):
    with open(file_path, "r") as handle:
        return json.load(handle)

def load_html_file(file_path):
    with open(file_path, "r") as handle:
        return handle.read()

def write_to_new_html_file(content):
    with open("animals.html", "w") as f:
        f.write(content)

def serialize_animal(fox):
    animal_repository_str=''
    animal_repository_str += f'<li class="cards__item">\n'
    animal_repository_str += f'<div class="card__title">\n'
    if "name" in fox:
        animal_repository_str += f'{fox['name']}</div>\n'
        animal_repository_str += f'<div class="card__text">\n'
        animal_repository_str += f'<ul>\n'
        if "taxonomy" in fox:
            if "scientific_name" in fox["taxonomy"]:
                animal_repository_str += f"<li><strong>Scientific name:</strong> {fox["taxonomy"]["scientific_name"]}</li>\n"
            if "characteristics" in fox:
                if "diet" in fox["characteristics"]:
                    animal_repository_str += f"<li><strong>Diet:</strong> {fox["characteristics"]["diet"]}</li>\n"
            if "locations" in fox:
                animal_repository_str += f"<li><strong>Location:</strong> {fox["locations"][0]}</li>\n"
            if "characteristics" in fox:
                if "type" in fox["characteristics"]:
                    animal_repository_str += f"<li><strong>Type:</strong> {fox["characteristics"]["type"]}</li>\n"
        #animal_repository_str+='</p>\n'
        animal_repository_str+='</ul>\n'
    else:
        animal_repository_str="ERROR: fox without a name"
    return animal_repository_str


def main():
    animals_data = load_animals_data("animals_data.json")
    html_data=load_html_file("animals_template.html")
    __replace__= "__REPLACE_ANIMALS_INFO__"


    fox_repository_string=""

    # for each type of fox in the input json file, create a repository string
    for fox in animals_data:
        fox_repository_string+=serialize_animal(fox)

    # The replacement below is necessary to avoid a mojibake
    fox_repository_string=fox_repository_string.replace("â€™","\'")
    # Replace the string to replace in the html with the animal repository
    html_data=html_data.replace(__replace__, fox_repository_string)

    write_to_new_html_file(html_data)
    #print(html_data)

if __name__ == "__main__":
    main()