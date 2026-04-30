"""
Algorithm:
=============================
step 10: show the menu and ask for input to select a function
step 20: validate the input, if not, return to step 10
step 30: execute the desired CRUD function or analysis function
step 40: show the results to screen
step 50: ask for an enter to continue
step 60: after enter is provided, start from 10 again.
"""

# File revision information: PA3
import os
import sqlite3
import statistics
import random
import sys
from typing import Optional

from thefuzz import fuzz
import matplotlib.pyplot as plt
import matplotlib
import sqlalchemy
import movie_detail_fetcher as mdf
import movie_storage_sql as mss
import user_storage_sql as uss
import web_generator as wg

matplotlib.use("Agg")

# from random import choice
# from time import time

# class BColors used for color setting of output text
# pylint: disable=too-few-public-methods
print("This is the movie database application. Please select a user profile to start.")
print("CWD:", os.getcwd())


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


CURRENT_USER_ID = -1
CURRENT_USERNAME = ""

# Constant used for the fuzzy search sensitivity. Adjust to higher level
# to focus the search quality
FUZZY_SENS = 65


def clear_screen():
    """
    Clean the screen before showing the menu. Does not seem to work well though on this terminal
    """
    if os.name == "nt":
        os.system("cls")
    else:
        # fallback if TERM not set
        if "TERM" in os.environ:
            os.system("clear")
        else:
            print("\n" * 100)


# Check if the content of the string is a float


def is_float(string: str) -> bool:
    """
    carefully check if a string can be converted to a float
    """
    try:
        float(string)
    except ValueError:
        return False
    return True


def show_menu():
    """
    Show the menu based on the menu_string and ask for input. Only allow valid input.
    """
    while True:
        clear_screen()  # clears the screen
        if CURRENT_USERNAME:
            print(
                BColors.MENU_TEXT
                + f"Welcome {CURRENT_USERNAME} to your movie database!"
                + BColors.ENDC
            )
        print(
            BColors.MENU_TEXT + "** ** ** ** ** My Movies Database ** ** ** ** ** \n\n"
        )
        for number, function in FUNCTIONS.items():
            print(BColors.MENU_TEXT + f"{number} - {function[1]}" + BColors.ENDC)
        try:
            user_choice = int(input(BColors.MENU_TEXT + "Enter choice(1 - 9): "))
            # print(user_choice)
            if user_choice in FUNCTIONS:
                # print("returning", FUNCTIONS[user_choice][0])
                return FUNCTIONS[user_choice][0]
        except (TypeError, ValueError):
            print(BColors.FAIL + "Please enter a valid choice!" + BColors.ENDC)


def shorten_string(long_string: str, max_length: int, break_right: int) -> str:
    """
    Shorten the poster link if it is too long for the screen, by slicing the string and
    adding ... in the middle. Also check that the length of the string is not shorter
    than 36, otherwise it would result in an error when slicing the string
    """
    # print(f"shortening string: {long_string} to max length {max_length} with
    # break_right {break_right}")
    if long_string is None:
        return ""
    if max_length - break_right - 3 < 0:
        return long_string[0:max_length]
    if len(long_string) > max_length:
        dot_space = max_length - break_right - 1
        if dot_space < 2:
            raise ValueError(
                f"Invalid input parameters max_length + should be at least {break_right + 3 - 1}"
            )
        if dot_space < 3:
            dots = ".."
        else:
            dots = "..."
        return (
            long_string[0 : max_length - break_right - len(dots)]
            + dots
            + long_string[-break_right:]
        )
        # -3 is for the ... and +1 is to include the character
        # at the position of max_length-break_off_right-3
    return long_string


def command_list_all_movies():
    """
    list the all available movies in the current DB
    """
    movies = mss.list_all_movies()
    print(BColors.LISTING + "Showing you now all movies in the DB")
    command_list_movies(movies)


# pylint: disable=dangerous-default-value
def command_list_movies(movie_list: Optional[list] = None):
    # This trick with optional list is needed to avoid a problem
    # of a list getting the value None
    # command_list_movies(movie_list:list=None)   => Results in a warning
    """
    list the all available movies in the current DB or list the provided movies
    """

    if (
        movie_list is None
    ):  # no list with movies is provided, so fetch the ones from the DB
        movie_list = []
        movie_list = list(mss.list_movies(CURRENT_USER_ID))
        # Type conversion needed as list_movies returns a Sequence
        print(BColors.LISTING + f"Showing you now {len(movie_list)} movie(s)")
        print(BColors.LISTING + f"{
                'ID':<5}|{
                'imdbID':<12}|{
                'Title':<35}|{
                    'Year':<12}|{
                        'imdbRating':<12}|{
                            'Poster link':<30}|{
                                'Notes':<20}")
        print(
            BColors.LISTING
            + "========================================================================"
            "=============================================================="
        )
        for movie in movie_list:
            print(BColors.LISTING + f"{
                    movie[0]:<5}|{
                    movie[1]:<12}|{
                    shorten_string(movie[2], 35, 6):<35}|{
                    movie[3]:<12}|{
                    movie[4]:<12}|{
                    shorten_string(movie[5], 30, 6):<30}|{
                    shorten_string(movie[6], 20, 6):<20}")
    else:  # a list with movies is provided, so show those
        try:
            print(BColors.LISTING + f"Showing you now {len(movie_list)} movie(s)")
            print(BColors.LISTING + f"{
                    'ID':<5}|{
                    'imdbID':<12}|{
                    'Title':<60.58}|{
                    'Year':<12}|{
                        'imdbRating':<12}|{
                            'Poster link':<2}")
            print(
                BColors.LISTING
                + "========================================================================"
                "======================================================================"
            )
            if len(movie_list) == 0:
                print(
                    BColors.LISTING
                    + "No movies found with the provided search criteria"
                )
                return
            if isinstance(movie_list[0], tuple) or isinstance(
                movie_list[0], sqlalchemy.engine.row.Row
            ):
                for movie in movie_list:
                    print(BColors.LISTING + f"{
                            movie[0]:<5}|{
                            movie[1]:<12}|{
                            movie[2]:<60.58}|{
                            movie[3]:<12}|{
                            movie[4]:<12}|{
                            shorten_string(movie[5],30,6):<30}")
            elif isinstance(movie_list[0], dict):
                counter = 1
                for movie in movie_list:
                    print(BColors.LISTING + f"{
                            counter:<5}|{
                            movie['imdbID']:<12}|{
                            movie['Title']:<60.58}|" f"{
                            movie['Year']:<12}|{
                            '-':<12}|{
                            shorten_string(movie['Poster'], 30, 6):<30}")
                    counter += 1
            else:
                raise TypeError("Unexpected Type", type(movie_list[0]))
        except (TypeError, KeyError) as e:
            print(BColors.WARNING + "Could not print the list of movies! Due to: ", e)
            print(BColors.WARNING + "going for a raw print instead")
            for movie in movie_list:
                print(BColors.WARNING + str(movie))


def enter_note() -> str:
    """
    Manually enter a note for the selected movie
    :return: a valid rating as float or -1 when the user pressed ENTER
    """
    note = input(BColors.INPUT_TEXT + "Enter a note for this movie: " + BColors.ENDC)
    return note


def enter_year() -> str:
    """
    Manually enter the year of the movie
    :return: a valid year as integer or -1 when the user pressed ENTER
    """
    while True:
        try:
            year_range = input(BColors.INPUT_TEXT + "Enter the year: ").strip()
            if year_range == "":
                return ""
            year = year_range.split("-")
            # print(year)
            for year in year_range:
                year = int(year)
                if year < 1888:  # the first year that a film was published
                    raise ValueError
                return year_range
            # in case no valid year, nor an ENTER was provided raise a ValueError
            return year_range
        except (TypeError, ValueError):
            print(
                BColors.FAIL
                + "Please enter a valid year of 4 digits, from 1888 onwards or a year "
                "range e.g 1977 - 1982" + BColors.ENDC
            )
            input(BColors.FAIL + "Press enter to continue!" + BColors.ENDC)


def enter_movie_title():
    """
    Manually enter the title of the movie
    :return: a valid rating as string which has a minimum length of 2 characters
    """
    while 1:
        title = input(BColors.INPUT_TEXT + "Enter movie title: ").strip()
        # Assuming there is no movie title with less than 2 characters.
        if len(title) >= 2:
            return title
        # If no proper title was entered with at least 2 characters:
        print(
            BColors.FAIL
            + "Please enter a valid movie title of at least 2 characters"
            + BColors.ENDC
        )


def fetch_movie_via_id(movie_index, movies_list) -> dict:
    """
    from a list of movies and a provided movie_index, return the specific
    movie that was chosen.
    :param movie_id:
    :param movies_found:
    :return:
    """
    # id is the index in the movies_list.
    try:
        movie = movies_list[movie_index]
        # print(
        # BColors.LISTING + f"This is the selected movie under id {movie_index}: \n{
        # movies_list[movie_index]}")
        return movie
    except KeyError:
        return {}


def select_movie(movies_found: list) -> dict:
    """
    from a list of movies and  input from a user, i.e. a
    movie ID, return the specific movie that was selected
    The user can abort by pressing ENTER.
    It is checked if the provided user input movie is indeed
    a valid ID, return the movie that was chosen.
    :param movies_found: a list of movies
    :return: 1 specific movie as dict or and empty dict if
    the user pressed enter
    """
    while 1:
        selected_id = input(
            BColors.INPUT_TEXT + "Enter movie valid ID or ENTER to abort: "
        ).strip()
        if selected_id == "":
            return {}
        try:
            selected_id = int(selected_id)
            selected_movie = fetch_movie_via_id(selected_id - 1, movies_found)
            if len(selected_movie) != 0:  # If a valid id was provided
                return selected_movie
        except ValueError:
            pass
        print(
            BColors.FAIL
            + "Please enter a valid movie id as number or press ENTER to abort"
            + BColors.ENDC
        )


def command_add_movie() -> bool:
    """
    Algorithm:
    1. get user input for title, year of release and imdbRating
    2. Check if similar titles are already present in the DB.
    3.      if yes, show the available movies and ask for input if the user wants to continue
    4.          if yes, add the movie to the DB.
    5.          If no, abort
    6.      If no, abort

        :return: bool : success or not
    """

    def enter_correct_movie_input() -> dict:
        """
        algorithm:
        1. Ask input for movie title.
        2. Check if the input is not empty, at least 1 character
        3. Find all movies containing the movie title
        4. Print all the found movies, including the imdbID, title and year
        5. Ask the user to enter the movie it wanted to insert
        6. For the provided imdbID, return the full title, the year and,
           if available, an imdbRating.

        :return: full title, the year and, if available, an imdbRating.
        """
        title = enter_movie_title()
        selected_movie = {}
        movies_found = mdf.fetch_movie_general_data(title)
        if len(movies_found) == 0:
            return {}
        command_list_movies(movies_found)
        selected_movie = select_movie(movies_found)
        if len(selected_movie) != 0:  # User selected a valid movie
            try:
                year = mdf.fetch_specific_movie_detail_item(
                    "Year", selected_movie["imdbID"]
                )
            except ValueError:
                year = 0
            try:
                rating = float(
                    mdf.fetch_specific_movie_detail_item(
                        "imdbRating", selected_movie["imdbID"]
                    )
                )
            except ValueError:
                rating = 0
            try:
                country = str(
                    mdf.fetch_specific_movie_detail_item(
                        "Country", selected_movie["imdbID"]
                    )
                )
            except ValueError:
                rating = 0
            movie = {
                "imdbID": selected_movie["imdbID"],
                "Title": selected_movie["Title"],
                "Year": year,
                "Rating": rating,
                "Poster": selected_movie["Poster"],
                "Country": country,
            }
            return movie
        # User pressed ENTER to abort
        return {}

    def add_the_movie(movie: dict) -> None:
        print(BColors.LISTING + "Storing the movie...")
        try:
            if not mss.add_movie(movie, CURRENT_USER_ID):
                raise sqlite3.IntegrityError(
                    BColors.WARNING + "Movie could not be "
                    "stored. Check if the imdbID is not stored already...."
                )
            print(BColors.LISTING + f"Movie '{movie['Title']}' successfully added.")
        except sqlite3.IntegrityError as error:
            print(
                BColors.WARNING
                + f"Movie {movie['Title']} not "
                + "stored successfully. Please contact your system administrator"
            )
            print(BColors.WARNING + f"Fault message is: {error}" + BColors.ENDC)

    # =======================================================================
    # The actual start of function command_add_movie
    # =======================================================================

    new_movie = enter_correct_movie_input()
    if len(new_movie) != 0:  # A valid imdbID was provided
        if len(new_movie["Title"]) != 0:
            movies_found = search_title(new_movie["Title"], 3)
            if len(movies_found) == 0:
                add_the_movie(new_movie)
            else:
                print(
                    BColors.INPUT_TEXT
                    + "The following similar movies already exist in the DB:"
                )
                command_list_movies(movies_found)
                choice = input("Do you want to continue y/n: ")
                if choice.lower() == "y":
                    add_the_movie(new_movie)


def select_movie_id() -> tuple:
    """
      Algorithm:
    1. Ask what movie do you want to select
    2. Check if the movie exist in the DB with the EXACT title match_type(0).
    3. If not found, check if there are similar movies in the DB match_type(3)
        show the movies with a number to the user and ask for input to select one
        return the id, title, year and imdbRating of the selected movie.
        If the user does not provide a valid number to select a movie. Return an empty
        tuple
    4. If 1 or more movies found:
        show the movies with a number to the user and ask for input to select one
        return the id, title, year and imdbRating of the selected movie
        If the user does not provide a valid number to select a movie. Return an empty
        tuple
    :return: (id,title,year,imdbRating) or tuple()
    """

    def show_found_movies_and_select(movies: list) -> tuple:
        command_list_movies(movies)
        valid_entry = False
        while valid_entry is False:
            try:
                movie_id = input(
                    BColors.INPUT_TEXT
                    + "Please provide ID of the movie you would like to select? "
                    "Or press Enter to return to MENU: "
                )
                if len(movie_id) == 0:
                    return tuple()
                for movie in movies:
                    if movie[0] == int(movie_id):
                        valid_entry = True
                        # print(BColors.LISTING + "Selected movie =", movie)
                        return movie
            except (ValueError, TypeError):
                pass
            print(
                BColors.WARNING
                + "Wrong input provided, please try again"
                + BColors.ENDC
            )

    # =======================================================================
    # The actual start of function select_movie_id
    # =======================================================================
    title = enter_movie_title()
    # CHECK IF A MOVIE WITH THIS TITLE EXISTS IN THE DB with this EXACT title
    movies_found = search_title(title, 0)
    if len(movies_found) >= 1:  # if the DB has 1 or more entries found
        selected_movie = show_found_movies_and_select(movies_found)
        if len(selected_movie) == 0:  # User pressed ENTER to escape
            print(BColors.WARNING + "The user aborted deletion!" + BColors.ENDC)
            return tuple()
        # The user selected the movie
        print(BColors.LISTING + f"Movie {selected_movie} was selected. " + BColors.ENDC)
        return selected_movie
    # No movies found. Searching for movies with similar name
    print(
        BColors.WARNING
        + "Movie not found. Searching for movies with "
        + "similar name..."
        + BColors.ENDC
    )
    movies_found = search_title(title, 3)
    if len(movies_found) > 0:  # If 1 or more similar movies found
        print(
            BColors.LISTING
            + "Found 1 or more movies with a similar name, please select"
        )
        selected_movie = show_found_movies_and_select(movies_found)
        if len(selected_movie) != 0:  # The user selected a movie
            return selected_movie
        # No movies with similar names found
        print(BColors.WARNING + "No movie found with that name in the DB.")
        return tuple()
    # if No movie found:
    print(
        BColors.WARNING + "Movie not found in the DB, nor movies with a similar name!"
    )
    return tuple()


def command_delete_movie() -> bool:
    """
    Algorithm:
    1. Ask what movie do you want to delete
    2. Check if the movie exist in the DB with the EXACT title match_type(0).
    3. If no movies found, check if there are similar movies in the DB match_type(3)
    4.      If there are no similar movies found, return false
    5.      If 1 or multiple similar movies found:
    6.          Show the movies with number to the user and for input, which number to
                delete or empty string to return to MENU
    7.          Delete the movie in the DB using the ID with the new imdbRating
    8. If multiple movies found: act like 6,7,8

    :return: a boolean if the movie was updated or not
    """
    selected_movie = select_movie_id()
    # print("This is the movie selected: ", selected_movie)
    # print("Type: ", type(selected_movie))
    if len(selected_movie) == 0:
        print(BColors.WARNING + "Delete aborted!" + BColors.ENDC)
        return False
    if mss.delete_movie(
        selected_movie[0], selected_movie[2], CURRENT_USER_ID
    ):  # check if the deletion was successful
        print(
            BColors.LISTING
            + f"Movie {selected_movie[2]} deleted successfully."
            + BColors.ENDC
        )
        return True
    # If deletion was not successful
    print(
        BColors.WARNING + f"Deleting movie {selected_movie[2]} failed..." + BColors.ENDC
    )
    return False


def command_update_movie() -> bool:
    """
    Algorithm:
    1. Ask what movie do you want to update
    2. Check if the movie exist in the DB with the EXACT title match_type(0).
    3. If no movies found, check if there are similar movies in the DB match_type(3)
    4.      If there are no similar movies found, return false
    5.      If 1 or multiple similar movies found:
    6.          Show the movies with number to the user and for input, which number to
                update or empty string to return to MENU
    7.          ask for the new imdbRating
    8.          Update the movie in the DB using the ID with the new imdbRating
    9. If multiple movies found: act like 6,7,8

    :return: a boolean if the movie was updated or not
    """

    selected_movie = select_movie_id()
    # print(f"The following movie will be updated: {selected_movie}")
    if len(selected_movie) == 0:
        print(BColors.WARNING + "Update aborted!" + BColors.ENDC)
        return False
    new_note = enter_note()
    if new_note == "":
        print(BColors.WARNING + "Update aborted!" + BColors.ENDC)
        return False
    if mss.update_movie(selected_movie[0], new_note, selected_movie[2]):
        # check if the update was successful
        print(f"Movie {
                selected_movie[2]} with ID{
                selected_movie[0]} updated successfully.")
        return True
    # If deletion was not successful
    print(BColors.WARNING + f"Updating of movie {selected_movie[2]} failed!")
    return False


def command_show_stats():
    """
    Algorithm:
    1. Get all the movies in the database
    2. Create a list of ratings of all the movies
    3. Derive the median and mean statistics by using statistics module
    4. Derive the max, min rating and best and worst movie by
    calling max_min_worst_best
    :return:
    """

    def max_min_worst_best_movie(movies, rating_list) -> tuple:
        """
        Gather the statistics from the films and imdbRating in the dict.
        Return best movie, worst movie, and the related imdbRating as tuple
        """
        min_rating = min(rating_list)
        max_rating = max(rating_list)
        worst_movie = ""
        best_movie = ""
        for movie in movies:
            if movie[4] == min_rating:
                # in case 2 or more movies have the worst imdbRating
                worst_movie += movie[2] + " + "
            if movie[4] == max_rating:
                # in case 2 or more movies have the best imdbRating
                best_movie += movie[2] + " + "
        if best_movie == "":
            best_movie = "Not found + "
        if worst_movie == "":
            worst_movie = "Not found + "
        return best_movie[0:-3], max_rating, worst_movie[0:-3], min_rating
        # slicing to remove the + at the end

    # =======================================================================
    # The actual start of function command_show_stats
    # =======================================================================

    rating_list = []
    movies = mss.list_all_movies()
    for movie in movies:
        rating_list.append(movie[4])
    # print(BColors.LISTING + f"Rating_list: {rating_list}" + BColors.ENDC)
    average_rating = statistics.mean(rating_list)
    median_rating = statistics.median(rating_list)
    best, max_rat, worst, min_rat = max_min_worst_best_movie(movies, rating_list)
    print(
        BColors.LISTING
        + "Showing you now the statistics of all movies in the DB"
        + BColors.ENDC
    )
    print(BColors.LISTING + f"Average imdbRating : {average_rating}" + BColors.ENDC)
    print(BColors.LISTING + f"Median imdbRating  : {median_rating}" + BColors.ENDC)
    print(BColors.LISTING + f"Best movie         : {best}, {max_rat}" + BColors.ENDC)
    print(BColors.LISTING + f"Worst movie        : {worst}, {min_rat}" + BColors.ENDC)
    print(BColors.ENDC)


def command_random_movie() -> tuple:
    """
    selects a random movie and returns a tuple including the movie title and it's imdbRating
    """
    # Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    movies = mss.list_all_movies()
    random_movie = random.choice(movies)
    print(BColors.LISTING + f"Your movie for tonight: {
            random_movie[2]}, it's rated {
            random_movie[4]}.")
    return random_movie


def editing_distance(search_string: str, movie_title: str) -> int:
    """NOT YET READY FOR MATCH_TYPE 4
    This function calculates the distance between the search_string and movie title
    and returns the "distance" between these 2 strings. The distance is calculated
    using fuzzy matching, using the "thefuzz" library. Currently not used.

    """
    distance = fuzz.ratio(search_string, movie_title)
    # print (distance)
    return distance


def search_title(search_string, match_type: int = 0) -> list:
    """
    searches for a title or part of the title  in the DB using the search_string
    and 4 search variants expressed by match_type (int)
    :param search_string:
    :param match_type:

      match_type 0 => not exact & case-insensitive
      match_type 1 => matching characters, but case-insensitive and stripped
      match_type 2 => exact match, and case-sensitive
      match_type 3 => fuzzy matching (not yet implemented)
    :return: a list with all the found movies
    """

    movies_found = []  # create an empty dict to be used by all the found movies
    try:
        if match_type > 3 or match_type < 0:
            raise ReferenceError(
                BColors.FAIL + "search function does not exist with that match_type"
            )
        movies_found = list(
            mss.search_movie(search_string, CURRENT_USER_ID, match_type)
        )
    except ReferenceError:
        print(BColors.WARNING + "Movie not found" + BColors.ENDC)

    return movies_found


def command_search_movie():
    """
    The user is asked to provide the title for a movie.
    it will then call search_title with match_type 3
    The results will be printed to screen
    :return:
    """
    title = enter_movie_title()
    movies_found = search_title(title, 3)

    command_list_movies(movies_found)


def command_sort_by_rating(direction: str = "descending") -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
    the function returns the sorted list ascending or descending, based upon input
    parameter 'direction'
    :param movies
    :param match_type:
    :return:
    """
    movie_list = mss.list_movies(CURRENT_USER_ID)

    descending = direction == "descending"
    # same as if direction == "descending": descending = True else False
    sorted_list = sorted(movie_list, key=lambda tup: tup[4], reverse=descending)
    print(
        BColors.LISTING
        + f"Showing you now all movies in the DB for {CURRENT_USERNAME} sorted by rating in {direction}"
    )
    command_list_movies(sorted_list)


def command_quit():
    """
    quits the application
    :return:
    """
    sys.exit()


def command_create_rating_histogram():
    """
    Creates a histogram of the ratings in the dict
    uses the following imports:
    import numpy as np
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    """
    rating_list = []
    movies = mss.list_all_movies()
    for movie in movies:
        rating_list.append(movie[4])
    plt.hist(rating_list)
    plt.title("Histogram of movie imdbRatings")
    plt.xlabel("value")
    plt.ylabel("frequency")
    plt.show()
    plt.savefig("histogram.png")
    sys.stdout.flush()
    print(BColors.LISTING + "File histogram.png is created")


def command_generate_webstie():
    """
    Generates a website with all the movies of the user, using the web_generator module
    """
    movies_this_user = mss.list_movies(CURRENT_USER_ID)
    print(
        BColors.LISTING
        + f"Generating website with all your movies ({len(movies_this_user)})..."
        + BColors.ENDC
    )
    f_name = wg.generate_website(movies_this_user, CURRENT_USERNAME)
    print(
        BColors.LISTING
        + "Website generated successfully. To view, open the file: \n"
        + f"{f_name}."
        + BColors.ENDC
    )


def command_create_new_user() -> tuple:
    """
    Asks the user to create a new user profile by providing a username and email address.
    It will then create a new user profile in the database and return the username and user_id of the created user.
    :return: username and user_id of the created user
    """
    username = input("Enter your username: ")
    email_address = input("Enter your email address: ")
    user_id = uss.add_user(username, email_address)
    if user_id != -1:
        print(
            BColors.LISTING
            + f"User profile for {username} created successfully."
            + BColors.ENDC
        )
        return user_id, username
    print(
        BColors.WARNING
        + f"Failed to create user profile for {username}. Exiting function."
        + BColors.ENDC
    )
    return -1, ""


def command_update_user_profile():
    """
    updates the user profile in the database by asking for the username and email address
    :return:
    """
    global CURRENT_USERNAME
    clear_screen()
    command_list_users()
    selected_user_id = input(
        "Enter the ID of the user you want to update or press ENTER to abort: "
    )
    if selected_user_id == "":
        print(BColors.WARNING + "User profile update aborted." + BColors.ENDC)
        return
    try:
        selected_user_id = int(selected_user_id)
        users = uss.list_users()
        for user in users:
            if user[0] == selected_user_id:
                orig_username = user[1]
                orig_email_address = user[2]
                break
        else:
            print(
                BColors.WARNING
                + "Invalid user ID provided. User profile update aborted."
                + BColors.ENDC
            )
            return
    except (ValueError, TypeError):
        print(
            BColors.WARNING
            + "Invalid input provided. User profile update aborted."
            + BColors.ENDC
        )
        return
    username = input(f"Enter a new username (was {orig_username}): ")
    if username == "":
        username = orig_username
        print(BColors.LISTING + f"Using original username: {username}" + BColors.ENDC)
    email_address = input(
        BColors.INPUT_TEXT
        + f"Enter a new email address (was {orig_email_address}): "
        + BColors.ENDC
    )
    if email_address == "":
        email_address = orig_email_address
        print(
            BColors.LISTING
            + f"Using original email address: {email_address}"
            + BColors.ENDC
        )
    if uss.update_user_profile(selected_user_id, username, email_address):
        print(
            BColors.LISTING
            + f"User profile for {username} updated successfully for user {selected_user_id}."
            + BColors.ENDC
        )
        if CURRENT_USER_ID == selected_user_id:
            CURRENT_USERNAME = username
    else:
        print(
            BColors.WARNING
            + f"Failed to update user profile for {CURRENT_USER_ID}."
            + BColors.ENDC
        )


def command_select_user() -> tuple:
    """
    Asks the user to select a user profile from the database. Returns the user_id of the selected user.
    If no users are available, it will ask to create a new user profile.
    if users are available, it will show the list of users and ask to select one by providing the user_id.
    if the user provides an invalid user_id, it will ask again until a valid
    user_id is provided or the user presses ENTER to abort.
    if the user presses ENTER to abort, it will return None.
    If the user selects to create a new user profile, it will ask for the
    username and email address and create a new user profile in the database.

    :return: user_id of the selected user or None if no user is selected
    """
    global CURRENT_USER_ID, CURRENT_USERNAME
    users = uss.list_users()
    if not users:
        print(
            BColors.WARNING
            + "No users found in the database. Please create a new user profile."
            + BColors.ENDC
        )
        user_id, username = command_create_new_user()
        if user_id != -1:
            print(
                BColors.LISTING
                + f"User profile for {username} created successfully."
                + BColors.ENDC
            )
            return user_id, username
        print(
            BColors.WARNING
            + f"Failed to create user profile for {username}. Exiting application."
            + BColors.ENDC
        )
        return -1, ""
    print(BColors.LISTING + "Available users:" + BColors.ENDC)
    for user in users:
        print(
            BColors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + BColors.ENDC
        )
    while True:
        try:
            selected_user_id = input(
                "Enter the ID of the user you want to select or type 'new' to create a new profile: "
            )
            if selected_user_id.lower() == "new":
                user_id, username = command_create_new_user()
                return user_id, username
            selected_user_id = int(selected_user_id)
            for user in users:
                if user[0] == selected_user_id:
                    CURRENT_USER_ID = selected_user_id
                    CURRENT_USERNAME = user[1]
                    return selected_user_id, user[1]
            print(
                BColors.WARNING
                + "Invalid user ID. Please try again."
                + BColors.ENDC
            )
        except (ValueError, TypeError):
            print(
                BColors.WARNING
                + "Please enter a valid integer for the user ID."
                + BColors.ENDC
            )


def command_list_users():
    """
    Lists all the users in the database by showing their user_id, username and email address.
    :return:
    """
    users = uss.list_users()
    if not users:
        print(BColors.WARNING + "No users found in the database." + BColors.ENDC)
    else:
        print(BColors.LISTING + "Available users:" + BColors.ENDC)
        for user in users:
            print(
                BColors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + BColors.ENDC
            )


def command_delete_user():
    """
    Deletes a user profile from the database by asking for the user_id of the user to delete.
    It will then delete the user profile and all the movies associated with that user from the database.
    :return:
    """

    def delete_all_movies_of_user(user_id: int):
        movies = mss.list_movies(user_id)
        for movie in movies:
            mss.delete_movie(movie[0], movie[2], user_id)

    global CURRENT_USER_ID, CURRENT_USERNAME
    users = uss.list_users()
    if not users:
        print(BColors.WARNING + "No users found in the database." + BColors.ENDC)
        return
    print(BColors.LISTING + "Available users:" + BColors.ENDC)
    for user in users:
        print(BColors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + BColors.ENDC)
    while True:
        try:
            selected_user_id = input(
                BColors.INPUT_TEXT
                + "Enter the ID of the user you want to delete or press ENTER to abort: "
                + BColors.ENDC
            )
            if selected_user_id == "":
                print(BColors.WARNING + "User deletion aborted." + BColors.ENDC)
                return
            selected_user_id = int(selected_user_id)
            for user in users:
                if user[0] == selected_user_id:
                    if uss.delete_user(selected_user_id):
                        delete_all_movies_of_user(selected_user_id)
                        print(
                            BColors.LISTING
                            + f"User {user[1]} and all associated movies deleted successfully."
                            + BColors.ENDC
                        )
                        if CURRENT_USER_ID == selected_user_id:
                            CURRENT_USER_ID = -1
                            CURRENT_USERNAME = ""
                            command_select_user()
                        print(
                            BColors.LISTING
                            + f"User {user[1]} deleted successfully."
                            + BColors.ENDC
                        )
                    else:
                        print(
                            BColors.WARNING
                            + f"Failed to delete user {user[1]}."
                            + BColors.ENDC
                        )
                    return
            print(BColors.WARNING + "Invalid user ID. Please try again." + BColors.ENDC)
        except (ValueError, TypeError):
            print(
                BColors.WARNING
                + "Please enter a valid integer for the user ID."
                + BColors.ENDC
            )


# pylint: disable=pointless-string-statement
"""
Function Dispatch Dictionary
"""
FUNCTIONS = {
    1: (command_list_movies, "List all my movies"),
    2: (command_list_all_movies, "List all movies in the database"),
    3: (command_add_movie, "Add movie"),
    4: (command_delete_movie, "Delete movie"),
    5: (command_update_movie, "Update movie with a note"),
    6: (command_show_stats, "Show movie statistics"),
    7: (command_random_movie, "Select a movie randomly"),
    8: (command_search_movie, "Search by title"),
    9: (command_sort_by_rating, "Movies sorted by rating"),
    10: (command_create_rating_histogram, "Create rating histogram"),
    11: (command_generate_webstie, "Generate the website"),
    12: (command_update_user_profile, "Update user profile"),
    13: (command_select_user, "Switch user"),
    14: (command_create_new_user, "Add user"),
    15: (command_list_users, "List users"),
    16: (command_delete_user, "Delete user"),
    0: (command_quit, "Exit"),
}


def main():
    """
    Order of the display of the menu and ask for user input to select an option
    :return:
    """
    clear_screen()

    global CURRENT_USER_ID, CURRENT_USERNAME
    selected_user_id, selected_username = (
        command_select_user()
    )  # ask the user to select a user profile, returns the user_id of the selected user
    CURRENT_USER_ID = selected_user_id
    CURRENT_USERNAME = selected_username
    print(
        BColors.LISTING
        + f"Selected user ID: {CURRENT_USER_ID}, username: {CURRENT_USERNAME}"
        + BColors.ENDC
    )

    if selected_user_id is None:
        print(
            BColors.FAIL + "No user selected, exiting the application." + BColors.ENDC
        )
        return
    while True:
        menu_selection = show_menu()
        menu_selection()
        input(BColors.INPUT_TEXT + "\nPress enter to continue")


if __name__ == "__main__":
    main()
