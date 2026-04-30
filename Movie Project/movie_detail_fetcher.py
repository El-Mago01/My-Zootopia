import os
import requests
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

BASE_URL = "https://www.omdbapi.com/"

api_key = os.getenv("apikey")

CURRENT_MOVIE = {}


class BColors:
    """Utility class to represent colors on the terminal."""

    HEADER = "\033[95m"
    MENU_TEXT = "\033[94m"
    OKCYAN = "\033[96m"
    INPUT_TEXT = "\033[92m"
    WARNING = "\033[93m"
    BLINKING = "\033[5m"
    FAIL = "\033[91m"
    LISTING = "\033[0m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def get_movie_data(imdbID: str = "", title: str = "") -> dict:
    """
    gets the detailed movie data from the OMDB API for a specific imdbID or title. At least
    one of these parameters must be provided with a valid value (i.e. not "").
    :param imdbID: the imdbID to fetch
    :param title: the title to fetch
    :return:
    """
    # print(f"imdbID={imdbID}, title={title}")

    def specify_search_term(imdbID: str = "0", title: str = "") -> str:
        try:
            if imdbID != "":  # the imdbID is the main search key
                search_term = f"?apikey={api_key}&i={imdbID}"
                # print(BColors.LISTING + f"imdbID={imdbID} provided. "
                #   " This is the search term:", search_term)
            elif title != "":  # the title is the main search key
                search_term = f"?apikey={api_key}&s={title}"
                # print(BColors.LISTING + "Title provided. This is the "
                # "search term:", search_term)
            else:
                search_term = f"?apikey={api_key}"
            return search_term
        # pylint: disable=broad-exception-caught
        # Any type of connection failure is caught
        except Exception as e:
            print(
                BColors.FAIL
                + "Unexpected path taken. Either imdbID or title must be provided"
                + BColors.ENDC
            )
            print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
            search_term = f"?apikey={api_key}"
            return search_term

    if imdbID != "":  # the imdbID is the main search key
        url = BASE_URL + specify_search_term(imdbID, "")
        # print(url)
    elif title != "":  # the title is the main search key
        url = BASE_URL + specify_search_term("", title)
        # print(url)
    else:
        return {}  # Should not occur. Either, imdbID or title must be provided
    try:
        response = requests.get(url, timeout=5)
        movie_details = response.json()
        # pylint: disable=broad-exception-caught
        # Any type of connection failure is caucht
    except Exception as e:
        print(BColors.FAIL + "Could not access API: GET Request failed:" + BColors.ENDC)
        print(BColors.FAIL + "Please contact your system administrator" + BColors.ENDC)
        print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
        movie_details = {}
        return movie_details
    if movie_details["Response"] == "False":  # the json contains an invalid response
        print(BColors.WARNING + "Movie not found!." + BColors.ENDC)
        movie_details = {}
    return movie_details


def fetch_movie_general_data(title: str) -> list:
    """
    get all the movies from the API that are alike the provided title
    :param title: the title to fetch
    :return: a list of movies
    """
    movie_data = get_movie_data("", title)
    if len(movie_data) > 0:
        return movie_data["Search"]
    return []  # in case movie_data is empty


def fetch_specific_movie_details(imdbID: str) -> dict:
    """
    fetch specific movie details from the OMDB API for a specific imdbID
    :param imdbID:
    :return:
    """
    movie_data = get_movie_data(imdbID)
    return movie_data


def fetch_specific_movie_detail_item(item: str, imdbID: str) -> str:
    """
    fetch specific movie details from the OMDB API for a specific imdbID and for a specific item,
    e.g. imdbRating
    :param item: the key you look for in the API-output e.g. imdbRating
    :param imdbID: the specific film you'd like to get the detailed data for.
    :return: the value of the provided item for the provided movie imdbID.
    or an empty string if the item is not found.
    """
    movie_details = {}
    try:
        movie_details = fetch_specific_movie_details(imdbID)
        # print(BColors.LISTING + "returning for item:" + BColors.ENDC, movie_details[item])
        if movie_details[item] is not None:
            return movie_details[item]
        return ""  # in case no movie_details for the specific imdbID where found
    except KeyError:
        print(BColors.FAIL + "Invalid item received: " + BColors.ENDC, movie_details)
        return ""


def main():
    """
    general test data to test basic functionality
    :return:
    """
    title = "matrix"
    movie_details = fetch_movie_general_data(title)
    print(f"Showing you now {len(movie_details)} movies")
    for movie in movie_details:
        print(f"{movie['imdbID']:<15}  - {movie['Title']:<40} - {movie['Year']:<10}")
    imdbID = "tt10838180"
    movie_details = fetch_specific_movie_details(imdbID)  # Best film EVER!!! :-)
    print(movie_details)
    try:
        year = int(fetch_specific_movie_detail_item("Year", imdbID))
    except (ValueError, TypeError):
        return
    print(year)


if __name__ == "__main__":
    main()
