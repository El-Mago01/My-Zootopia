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
import random
import sys
from typing import Optional
from thefuzz import fuzz
import matplotlib
import sqlalchemy
from user_interface import Bcolors
import movie_detail_fetcher as mdf
import movie_storage as ms
import web_generator as wg
import movie_analysis as ma
import user_handling as uh
import user_interface as ui


matplotlib.use("Agg")

# from random import choice
# from time import time

# class Bcolors used for color setting of output text
# pylint: disable=too-few-public-methods
print("This is the movie database application. Please select a user profile to start.")
print("CWD:", os.getcwd())




class MovieStorageError(Exception):
    """Raised when a movie can not be stored in the movie storage."""
    pass


# Constant used for the fuzzy search sensitivity. Adjust to higher level
# to focus the search quality
FUZZY_SENS = 65


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
        ui.clear_screen()  # clears the screen
        current_userid, current_username = uh.get_current_user()
        if current_username:
            print(
                ui.Bcolors.MENU_TEXT
                + f"Welcome {current_username} to your movie database!"
                + ui.Bcolors.ENDC
            )
        print(
            Bcolors.MENU_TEXT + "** ** ** ** ** My Movies Database ** ** ** ** ** \n\n"
        )
        for number, function in FUNCTIONS.items():
            print(Bcolors.MENU_TEXT + f"{number} - {function[1]}" + Bcolors.ENDC)
        try:
            user_choice = int(input(Bcolors.MENU_TEXT + "Enter choice(1 - 9): "))
            # print(user_choice)
            if user_choice in FUNCTIONS:
                # print("returning", FUNCTIONS[user_choice][0])
                return FUNCTIONS[user_choice][0]
        except (TypeError, ValueError):
            print(Bcolors.FAIL + "Please enter a valid choice!" + Bcolors.ENDC)


def shorten_string(long_string: str, max_length: int, break_right: int) -> str:
    """
    Shorten the poster link if it is too long for the screen, by slicing the string and
    adding ... in the middle. Also check that the length of the string is not shorter
    than 36, otherwise it would result in an error when slicing the string
    """
    # print(f"shortening string: {long_string} to max length
    # {max_length} with break_right {break_right}")
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
    movies = ms.fetch_all_movies()
    print(Bcolors.LISTING + "Showing you now all movies in the DB")
    command_list_movies(movies)


# pylint: disable=dangerous-default-value
def command_list_movies(movie_list: Optional[list] = None):
    # This trick with optional list is needed to avoid a problem
    # of a list getting the value None
    # command_list_movies(movie_list:list=None)   => Results in a warning
    """
    list the all available movies in the current DB or list the provided movies
    """
    current_userid, current_username = uh.get_current_user()
    if movie_list is None:  # no list with movies is provided, so fetch the ones from the DB
        movie_list = []
        movie_list = list(ms.fetch_movies(current_userid))
        print(Bcolors.LISTING +"THIS IS THE MOVIE LIST FOR ", current_username)
        # Type conversion needed as list_movies returns a Sequence
        print(Bcolors.LISTING + f"Showing you now {len(movie_list)} movie(s):")
        print(Bcolors.LISTING + f"{
                'ID':<5}|{
                'imdbID':<12}|{
                'Title':<35}|{
                'Year':<12}|{
                'imdbRating':<12}|{
                'Poster link':<32}|{
                'Notes':<32}|{
                'Country':<32}")
        print(
            Bcolors.LISTING
            + "========================================================================"
            "=========================================================================="
            "================="
        )
        for movie in movie_list:
            print(Bcolors.LISTING + f"{
                    movie[0]:<5}|{
                    movie[2]:<12}|{
                    shorten_string(movie[3], 35, 6):<35}|{
                    movie[4]:<12}|{
                    movie[5]:<12}|{
                    shorten_string(movie[6], 30, 6):<32}|{
                    shorten_string(movie[7], 30, 6):<32}|{
                    shorten_string(movie[8], 30, 6):<32}")
    else:  # a list with movies is provided, so show those
        try:
            print(Bcolors.LISTING + f"Showing now {len(movie_list)} movie(s) to "
                                    f"{current_username}.")
            print(Bcolors.LISTING + f"{
                    'ID':<5}|{
                    'imdbID':<12}|{
                    'Title':<35.58}|{
                    'Year':<12}|{
                    'imdbRating':<12}|{
                    'Poster link':<32}|{
                    'Notes':<32}|{
                    'Country':<32}")
            print(
                Bcolors.LISTING
                + "========================================================================"
                  "=========================================================================="
                  "================="
            )
            if len(movie_list) == 0:
                print(
                    Bcolors.LISTING
                    + "No movies found with the provided search criteria"
                )
                return
            if isinstance(movie_list[0], tuple) or isinstance(
                movie_list[0], sqlalchemy.engine.row.Row
            ) or isinstance(movie_list[0], list):
                for movie in movie_list:
                    # print("This movie will be plotted: ", movie)
                    print(Bcolors.LISTING + f"{
                            movie[0]:<5}|{
                            movie[2]:<12}|{
                            shorten_string(movie[3], 35, 6):<35}|{
                            movie[4]:<12}|{
                            movie[5]:<12}|{
                            shorten_string(movie[6],30,6):<32}{
                            shorten_string(movie[7], 30, 6):<32}|{
                            shorten_string(movie[8], 30, 6):<32}")

            elif isinstance(movie_list[0], dict):
                counter = 1
                for movie in movie_list:
                    print(Bcolors.LISTING + f"{
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
            print(Bcolors.WARNING + "Could not print the list of movies! Due to: ", e)
            print(Bcolors.WARNING + "going for a raw print instead")
            for movie in movie_list:
                print(Bcolors.WARNING + str(movie))


def enter_note() -> str:
    """
    Manually enter a note for the selected movie
    :return: a valid rating as float or -1 when the user pressed ENTER
    """
    note = input(Bcolors.INPUT_TEXT + "Enter a note for this movie: " + Bcolors.ENDC)
    return note


def enter_year() -> str:
    """
    Manually enter the year of the movie
    :return: a valid year as integer or -1 when the user pressed ENTER
    """
    while True:
        try:
            year_range = input(Bcolors.INPUT_TEXT + "Enter the year: ").strip()
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
                Bcolors.FAIL
                + "Please enter a valid year of 4 digits, from 1888 onwards or a year "
                "range e.g 1977 - 1982" + Bcolors.ENDC
            )
            input(Bcolors.FAIL + "Press enter to continue!" + Bcolors.ENDC)


def enter_movie_title():
    """
    Manually enter the title of the movie
    :return: a valid rating as string which has a minimum length of 2 characters
    """
    while 1:
        title = input(Bcolors.INPUT_TEXT + "Enter movie title: ").strip()
        # Assuming there is no movie title with less than 2 characters.
        if len(title) >= 2:
            return title
        # If no proper title was entered with at least 2 characters:
        print(
            Bcolors.FAIL
            + "Please enter a valid movie title of at least 2 characters"
            + Bcolors.ENDC
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
        # Bcolors.LISTING + f"This is the selected movie under id {movie_index}: \n{
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
            Bcolors.INPUT_TEXT + "Enter movie valid ID or ENTER to abort: "
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
            Bcolors.FAIL
            + "Please enter a valid movie id as number or press ENTER to abort"
            + Bcolors.ENDC
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
                country = ""
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
        print(Bcolors.LISTING + "Storing the movie...")
        current_userid, current_username = uh.get_current_user()
        try:
            if not ms.add_movie(movie, current_userid):
                raise MovieStorageError(
                    Bcolors.WARNING + "Movie could not be "
                    "stored. Check if the imdbID is not stored already...."
                )
            print(Bcolors.LISTING + f"Movie '{movie['Title']}' successfully added.")
        except MovieStorageError as error:
            print(
                Bcolors.WARNING
                + f"Movie {movie['Title']} not "
                + "stored successfully. Please contact your system administrator"
            )
            print(Bcolors.WARNING + f"Fault message is: {error}" + Bcolors.ENDC)

    # =======================================================================
    # The actual start of function command_add_movie
    # =======================================================================

    new_movie = enter_correct_movie_input()
    if len(new_movie) != 0:  # A valid imdbID was provided
        if len(new_movie["Title"]) != 0:
            # movies_found = search_title(new_movie["Title"], 3)
            movies_found = ""
            if len(movies_found) == 0:
                add_the_movie(new_movie)
            else:
                print(
                    Bcolors.INPUT_TEXT
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
                    Bcolors.INPUT_TEXT
                    + "Please provide ID of the movie you would like to select? "
                    "Or press Enter to return to MENU: "
                )
                if len(movie_id) == 0:
                    return tuple()
                for movie in movies:
                    if movie[0] == int(movie_id):
                        valid_entry = True
                        return movie
            except (ValueError, TypeError):
                pass
            print(
                Bcolors.WARNING
                + "Wrong input provided, please try again"
                + Bcolors.ENDC
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
            print(Bcolors.WARNING + "The user aborted deletion!" + Bcolors.ENDC)
            return tuple()
        # The user selected the movie
        print(Bcolors.LISTING + f"Movie {selected_movie} was selected. " + Bcolors.ENDC)
        return selected_movie
    # No movies found. Searching for movies with similar name
    print(
        Bcolors.WARNING
        + "Movie not found. Searching for movies with "
        + "similar name..."
        + Bcolors.ENDC
    )
    movies_found = search_title(title, 3)
    if len(movies_found) > 0:  # If 1 or more similar movies found
        print(
            Bcolors.LISTING
            + "Found 1 or more movies with a similar name, please select"
        )
        selected_movie = show_found_movies_and_select(movies_found)
        if len(selected_movie) != 0:  # The user selected a movie
            return selected_movie
        # No movies with similar names found
        print(Bcolors.WARNING + "No movie found with that name in the DB.")
        return tuple()
    # if No movie found:
    print(
        Bcolors.WARNING + "Movie not found in the DB, nor movies with a similar name!"
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
        print(Bcolors.WARNING + "Delete aborted!" + Bcolors.ENDC)
        return False
    if ms.delete_movie(
        selected_movie[0], selected_movie[2], uh.get_current_userid()
    ):  # check if the deletion was successful
        return True
    # If deletion was not successful
    print(
        Bcolors.WARNING + f"Deleting movie {selected_movie[2]} failed..." + Bcolors.ENDC
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
        print(Bcolors.WARNING + "Update aborted!" + Bcolors.ENDC)
        return False
    new_note = enter_note()
    if new_note == "":
        print(Bcolors.WARNING + "Update aborted!" + Bcolors.ENDC)
        return False
    if ms.update_movie(selected_movie[0], new_note, selected_movie[2]):
        # check if the update was successful
        print(f"Movie {
                selected_movie[2]} with ID{
                selected_movie[0]} updated successfully.")
        return True
    # If deletion was not successful
    print(Bcolors.WARNING + f"Updating of movie {selected_movie[2]} failed!")
    return False




def command_random_movie() -> tuple:
    """
    selects a random movie and returns a tuple including the movie title and it's imdbRating
    """
    # Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    movies = ms.fetch_all_movies()
    random_movie = random.choice(movies)
    print(Bcolors.LISTING + f"Your movie for tonight: {
            random_movie[3]}, it's rated {
            random_movie[5]}.")
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
                Bcolors.FAIL + "search function does not exist with that match_type"
            )
        movies_found = list(
            ms.search_movie(search_string, uh.get_current_userid(), match_type)
        )
    except ReferenceError:
        print(Bcolors.WARNING + "Movie not found" + Bcolors.ENDC)

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

def command_filter_movie():
    """
    Here the user can filter movies based on:
    - a minimum rating
    - a starting year
    - an ending year

    After the filtering, the user get displayed his film based
    on the filter
    """
    def get_user_input():
        while True:
            m_rating = input("What is the minimum rating: ").strip()
            if len(m_rating) == 0:
                m_rating = 0
                break
            try:
                m_rating = float(m_rating)
                break
            except ValueError:
                print("please enter a number or press enter: ")
        while True:
            while True:
                s_year = input("What is the starting year: ").strip()
                if len(s_year) == 0:
                    s_year=1850
                    break
                try:
                    s_year = int(s_year)
                    break
                except ValueError:
                    print("please enter a number or press enter: ")
            while True:
                e_year = input("What is the ending year: ").strip()
                if len(e_year) == 0:
                    e_year=3001
                    break
                try:
                    e_year = int(e_year)
                    break
                except ValueError:
                    print("please enter a number or press enter: ")
            if e_year >= s_year:
                break
            print("Please ensure ending year is larger than starting year")
        return m_rating, s_year, e_year

    min_rating, start_year, end_year = get_user_input()

    all_movies = ms.fetch_movies(uh.get_current_userid())
    filtered_movies = []
    for movie in all_movies:
        try:
            if '-' in movie[4]:
                from_year, to_year = movie[4].split('-')
                to_year = int(to_year)
            elif '–' in movie[4]:
                from_year, to_year = movie[4].split('–')
                to_year = int(to_year)
            else:
                to_year = int(movie[4])
        except ValueError:
            print(f"The movie {movie[3]}, has an incompatible format for year: {movie[4]}")
            return
        if movie[5] >= min_rating and end_year >= to_year >= start_year:
            filtered_movies.append(movie)
    command_list_movies(filtered_movies)


def command_sort_by_year(direction: str = "descending") -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[4] ensures the sorting on the year
    the function returns the sorted list ascending or descending, based upon input
    parameter 'direction'
    :param movies
    :param match_type:
    :param direction (either descending or ascending)
    :return:
    """
    movie_list = ms.fetch_movies(uh.get_current_userid())

    descending = direction == "descending"
    # same as if direction == "descending": descending = True else False
    sorted_list = sorted(movie_list, key=lambda tup: tup[4], reverse=descending)
    print(
        Bcolors.LISTING
        + f"Showing you now all movies in the DB for {uh.get_current_userid()} "
          f"sorted by year in {direction}"
    )
    command_list_movies(sorted_list)

def command_sort_by_rating(direction: str = "descending") -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
    the function returns the sorted list ascending or descending, based upon input
    parameter 'direction'
    :param movies
    :param match_type:
    :param direction (either descending or ascending)
    :return:
    """
    movie_list = ms.fetch_movies(uh.get_current_userid())

    descending = direction == "descending"
    # same as if direction == "descending": descending = True else False
    sorted_list = sorted(movie_list, key=lambda tup: tup[5], reverse=descending)
    current_user_id, current_user_name = uh.get_current_user()
    print(
        Bcolors.LISTING
        + f"Showing you now all movies in the DB for {current_user_name} "
          f"sorted by rating in {direction}"
    )
    command_list_movies(sorted_list)


def command_quit():
    """
    quits the application
    :return:
    """
    sys.exit()


def command_generate_website():
    """
    Generates a website with all the movies of the user, using the web_generator module
    """
    movies_this_user = ms.fetch_movies(uh.get_current_userid())
    print(
        Bcolors.LISTING
        + f"Generating website with all your movies ({len(movies_this_user)})..."
        + Bcolors.ENDC
    )
    current_user_id, current_user_name = uh.get_current_user()
    f_name = wg.generate_website(movies_this_user, current_user_name)
    print(
        Bcolors.LISTING
        + "Website generated successfully. To view, open the file: \n"
        + f"{f_name}."
        + Bcolors.ENDC
    )


# pylint: disable=pointless-string-statement
"""
Function Dispatch Dictionary
"""
FUNCTIONS = {
    1: (command_list_movies, "List all my movies"),
    2: (command_list_all_movies, "List all movies of all users"),
    3: (command_add_movie, "Add movie"),
    4: (command_delete_movie, "Delete movie"),
    5: (command_update_movie, "Update movie with a note"),
    6: (ma.command_show_stats, "Show movie statistics"),
    7: (command_random_movie, "Select a movie randomly"),
    8: (command_search_movie, "Search by title"),
    9: (command_filter_movie, "filter movies: by year / rating"),
    10: (command_sort_by_rating, "Movies sorted by rating"),
    11: (command_sort_by_year, "Movies sorted by year"),
    12: (ma.command_create_rating_histogram, "Create rating histogram"),
    13: (command_generate_website, "Generate the website"),
    14: (uh.command_update_user_profile, "Update user profile"),
    15: (uh.command_select_user, "Switch user"),
    16: (uh.command_create_new_user, "Add user"),
    17: (uh.command_list_users, "List users"),
    18: (uh.command_delete_user, "Delete user"),
    0: (command_quit, "Exit"),
}


def main():
    """
    Order of the display of the menu and ask for user input to select an option
    :return:
    """
    ui.clear_screen()



    selected_user_id, selected_username = (
        uh.command_select_user()
    )  # ask the user to select a user profile, returns the user_id of the selected user


    print(
        Bcolors.LISTING
        + f"Selected user ID: {selected_user_id}, username: {selected_username}"
        + Bcolors.ENDC
    )

    if selected_user_id is None:
        print(
            Bcolors.FAIL + "No user selected, exiting the application." + Bcolors.ENDC
        )
        return
    while True:
        menu_selection = show_menu()
        menu_selection()
        input(Bcolors.INPUT_TEXT + "\nPress enter to continue")


if __name__ == "__main__":
    main()
