import requests
import os
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

BASE_URL = "https://www.omdbapi.com/"

api_key = os.getenv('apikey')

CURRENT_MOVIE = {}


def get_movie_data(imdbID: str = "", title: str = "") -> dict:
    print(f"imdbID={imdbID}, title={title}")

    def specify_search_term(imdbID: str = "0", title: str = "") -> str:
        try:
            if imdbID != "":  # the imdbID is the main search key
                search_term = f"?apikey={api_key}&i={imdbID}"
                print(
                    f"imdbID={imdbID} provided. This is the search term:",
                    search_term)
            elif title != "":  # the title is the main search key
                search_term = f"?apikey={api_key}&s={title}"
                print("title provided. This is the search term:", search_term)
            return search_term
        except Exception as e:
            print("Unexpected path taken. Either imdbID or title must be provided")
            print(e)
            search_term = f"?apikey={api_key}"
            return search_term

    if imdbID != "":  # the imdbID is the main search key
        url = BASE_URL + specify_search_term(imdbID, "")
        print(url)
    elif title != "":    # the title is the main search key
        url = BASE_URL + specify_search_term("", title)
        print(url)
    try:
        response = requests.get(url)
        movie_details = response.json()
    except Exception as e:
        print("Could not access API: GET Request failed:", e)
        print("Please contact your system administrator")
        movie_details = {}
        return movie_details
    if movie_details['Response'] == "False":  # the json contains an invalid response
        print("Movie not found!.", movie_details['Error'])
        movie_details = {}
    else:
        print("Valid response received: ", movie_details['Response'])
    return movie_details


def fetch_movie_general_data(title: str) -> list:
    movie_data = get_movie_data("", title)
    print(movie_data)
    print(type(movie_data))
    if len(movie_data) > 0:
        return movie_data['Search']
    else:
        return []


def fetch_specific_movie_details(imdbID: str) -> dict:
    movie_data = get_movie_data(imdbID)
    return movie_data


def fetch_specific_movie_detail_item(item: str, imdbID: str) -> str:
    try:
        movie_details = fetch_specific_movie_details(imdbID)
        print("returning for item:", movie_details[item])
        if movie_details[item] is not None:
            return movie_details[item]
        else:
            return ""
    except KeyError:
        print("Invalid item received: ", movie_details)
        return ""


def main():
    title = "matrix"
    movie_details = fetch_movie_general_data(title)
    print(f"Showing you now {len(movie_details)} movies")
    for movie in movie_details:
        print(
            f"{movie['imdbID']:<15}  - {movie['Title']:<40} - {movie['Year']:<10}")
    imdbID = "tt10838180"
    movie_details = fetch_specific_movie_details(
        imdbID)  # Best film EVER!!! :-)
    print(movie_details)
    try:
        year = int(fetch_specific_movie_detail_item('Year', imdbID))
    except (ValueError, TypeError):
        return
    print(year)


if __name__ == "__main__":
    main()
