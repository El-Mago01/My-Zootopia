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
from thefuzz import fuzz
import matplotlib.pyplot as plt
import matplotlib
import sqlalchemy
from typing import Optional
import movie_detail_fetcher as mdf
import movie_storage_sql as mss
import user_storage_sql as uss
import web_generator as wg
matplotlib.use('Agg')

# from random import choice
# from time import time

# class BColors used for color setting of output text
# pylint: disable=too-few-public-methods
class BColors:
    """Utility class to represent colors on the terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

current_user_id = -1
current_username = ""

# Constant used for the fuzzy search sensitivity. Adjust to higher level
# to focus the search quality
FUZZY_SENS = 65


def clear_screen():
    """
    Clean the screen before showing the menu. Does not seem to work well though on this terminal
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        # fallback if TERM not set
        if 'TERM' in os.environ:
            os.system('clear')
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
        if current_username:
            print(
                BColors.OKGREEN +
                f"Welcome {current_username} to your movie database!" +
                BColors.ENDC)
        print(
            BColors.OKBLUE +
            "** ** ** ** ** My Movies Database ** ** ** ** ** \n\n")
        for key in FUNCTIONS:
            print(BColors.OKBLUE +
                  f"{key} - {FUNCTIONS[key][1]}" +
                  BColors.ENDC)
        try:
            user_choice = int(input(BColors.OKBLUE + "Enter choice(1 - 9): "))
            print(user_choice)
            if user_choice in FUNCTIONS:
                print("returning", FUNCTIONS[user_choice][0])
                return FUNCTIONS[user_choice][0]
        except (TypeError, ValueError):
            print(BColors.FAIL + "Please enter a valid choice!" + BColors.ENDC)


def command_list_all_movies():
    """
    list the all available movies in the current DB
    """
    movies = mss.list_all_movies()
    print(BColors.ENDC + f"Showing you now all movies in the DB")
    command_list_movies(movies)

# pylint: disable=dangerous-default-value
def command_list_movies(movie_list: Optional[list] = None): # This trick is needed to avoid a problem 
                                                            # of a list getting the value None 
                                                            # command_list_movies(movie_list:list=None)   => Results in a warning 
    """
    list the all available movies in the current DB or list the provided movies
    """
    if movie_list == None:  # no list with movies is provided, so fetch the ones from the DB
        movie_list = mss.list_movies(current_user_id)
        print(BColors.ENDC + f"Showing you now {len(movie_list)} movie(s)")
        print(
            BColors.ENDC + f"{
                'ID':<5}|{
                'imdbID':<12}|{
                'Title':<60}|{
                    'Year':<12}|{
                        'imdbRating':<12}|{
                            'Poster link':<2}")
        print(
            "========================================================================"
            "==============================================================")
        for movie in movie_list:
            print(
                BColors.ENDC + f"{
                    movie[0]:<5}|{
                    movie[1]:<12}|{
                    movie[2]:<60.58}|{
                    movie[3]:<12}|{
                        movie[4]:<12}|{
                            movie[5][0:26]}...{movie[5][-36:]:<2.50}")
    else: # a list with movies is provided, so show those
        try:
            print(BColors.ENDC + f"Showing you now {len(movie_list)} movie(s)")
            print(
                BColors.ENDC + f"{
                    'ID':<5}|{
                    'imdbID':<12}|{
                    'Title':<60.58}|{
                    'Year':<12}|{
                        'imdbRating':<12}|{
                            'Poster link':<2}")
            print(
                "========================================================================"
                "======================================================================")
            if len(movie_list) == 0:
                print(BColors.ENDC + f"No movies found with the provided search criteria")
                return
            if (isinstance(movie_list[0], tuple) or
                    isinstance(movie_list[0], sqlalchemy.engine.row.Row)):
                for movie in movie_list:
                    if len(movie[5]) > 36: # Ensure that poster link is not too long for the screen, if it is, shorten it with ... in the middle 
                                           # Also check that the length of the poster link is not shorter than 36, otherwise it would result in an 
                                           # error when slicing the string
                        poster = movie[5][0:26] + "..." + movie[5][-36:]
                    else:
                        poster = movie[5]
                    print(
                        BColors.ENDC + f"{
                            movie[0]:<5}|{
                            movie[1]:<12}|{
                            movie[2]:<60.58}|{
                            movie[3]:<12}|{
                            movie[4]:<12}|{
                            poster::<2.50}")
            elif isinstance(movie_list[0], dict):
                counter = 1
                for movie in movie_list:
                    print(
                        BColors.ENDC + f"{
                            counter:<5}|{
                            movie['imdbID']:<12}|{
                            movie['Title']:<60.58}|" f"{
                            movie['Year']:<12}|{
                            '-':<12}|{
                            movie['Poster'][0:26]}...{movie['Poster'][-36:]::<2.50}")
                    counter += 1
            else:
                raise TypeError("Unexpected Type", type(movie_list[0]))
        except (TypeError, KeyError) as e:
            print("Could not print the list of movies! Due to: ", e)
            print("going for a raw print instead")
            for movie in movie_list:
                print(movie)
                print(type(movie))


def enter_rating() -> float:
    """
    Manually enter the rating for the movie
    :return: a valid rating as float or -1 when the user pressed ENTER
    """
    while True:
        try:
            rating = input("Enter movie rating: ").strip()
            if rating == "":
                return -1
            rating = float(rating)
            if 0 <= rating <= 10:
                return rating
            # in case no valid rating, nor an ENTER was provided raise a ValueError
            raise ValueError
        except (TypeError, ValueError):
            print(
                BColors.FAIL +
                'Please enter a valid rating value from 0-10 or Enter to abort' +
                BColors.ENDC)


def enter_year() -> str:
    """
    Manually enter the year of the movie
    :return: a valid year as integer or -1 when the user pressed ENTER
    """
    while True:
        try:
            year_range = input(BColors.OKGREEN + "Enter the year: ").strip()
            if year_range == "":
                return ""
            year=year_range.split("-")
            print(year)
            print(type(year))
            for year in year_range:
                year = int(year)
                if year < 1888: # the first year that a film was published
                    raise ValueError
                return year_range
            # in case no valid year, nor an ENTER was provided raise a ValueError
            return year_range
        except (TypeError, ValueError):
            print(
                BColors.FAIL +
                "Please enter a valid year of 4 digits, from 1888 onwards or a year "
                "range e.g 1977 - 1982" +
                BColors.ENDC)
            input(BColors.FAIL + "Press enter to continue!" + BColors.ENDC)


def enter_movie_title():
    """
    Manually enter the title of the movie
    :return: a valid rating as string which has a minimum length of 2 characters
    """
    while 1:
        title = input(BColors.OKGREEN + "Enter movie title: ").strip()
        # Assuming there is no movie title with less than 2 characters.
        if len(title) >= 2:
            return title
        # If no proper title was entered with at least 2 characters:
        print(
            BColors.FAIL +
            "Please enter a valid movie title of at least 2 characters" +
            BColors.ENDC)

def fetch_movie_via_id(movie_index, movies_list) -> dict:
    """
    from a list of movies and a provided movie_index, return the specific
    movie that was chosen.
    :param movie_id:
    :param movies_found:
    :return:
    """
    print(f"{movie_index}These were the movies found:, {movies_list}")
    print(type(movies_list))
    # id is the index in the movies_list.
    try:
        movie=movies_list[movie_index]
        print(
            f"This is the selected movie under id {movie_index}: \n{
                movies_list[movie_index]}")
        return movie
    except KeyError:
        return {}

def select_movie(movies_found:list) -> dict:
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
            BColors.OKGREEN +
            "Enter movie valid ID or ENTER to abort: ").strip()
        if selected_id == "":
            return {}
        try:
            selected_id = int(selected_id)
            print(selected_id)
            selected_movie = fetch_movie_via_id(selected_id - 1, movies_found)
            if len(selected_movie) != 0:  # If a valid id was provided
                return selected_movie
        except ValueError:
            pass
        print(
            BColors.FAIL +
            "Please enter a valid movie id as number or press ENTER to abort" +
            BColors.ENDC)

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
        selected_movie=select_movie(movies_found)
        if len(selected_movie) != 0:  # User selected a valid movie
            try:
                year = mdf.fetch_specific_movie_detail_item(
                        'Year', selected_movie['imdbID'])
            except ValueError:
                year = 0
            try:
                rating = float(
                    mdf.fetch_specific_movie_detail_item(
                        'imdbRating', selected_movie['imdbID']))
            except ValueError:
                rating = 0
            print(selected_movie)
            movie = {'imdbID': selected_movie['imdbID'],
                     'Title': selected_movie['Title'],
                     'Year': year,
                     'Rating': rating,
                     'Poster': selected_movie['Poster']}
            return movie
        # User pressed ENTER to abort
        return {}

    def add_the_movie(movie: dict) -> None:
        print("Storing the movie")
        try:
            if not mss.add_movie(movie, current_user_id):
                raise sqlite3.IntegrityError(
                    "Movie could not be stored. Check if the imdbID is not yet already stored.")
            print(f"Movie \'{movie['Title']}\' successfully added")
        except sqlite3.IntegrityError as error:
            print(
                f"Movie {
                    movie['Title']} not stored successfully. Please contact your "
                f"system administrator")
            print("Fault message is: ", error)

    new_movie = enter_correct_movie_input()
    if len(new_movie) != 0:  # A valid imdbID was provided
        if len(new_movie['Title']) != 0:
            movies_found = search_title(new_movie['Title'], 3)
            if len(movies_found) == 0:
                add_the_movie(new_movie)
            else:
                print(
                    BColors.ENDC +
                    "The following similar movies already exist in the DB:")
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
                    f"Please provide ID of the movie you would like to select? "
                    f"Or press Enter to return to MENU: ")
                if len(movie_id) == 0:
                    return tuple()
                for movie in movies:
                    if movie[0] == int(movie_id):
                        valid_entry = True
                        print("Selected movie =", movie)
                        return movie
            except (ValueError, TypeError):
                pass
            print(
                BColors.WARNING +
                "Wrong input provided, please try again" +
                BColors.ENDC)

    # =======================================================================
    # The actual start of function select_movie_id
    # =======================================================================
    title = enter_movie_title()
    # CHECK IF A MOVIE WITH THIS TITLE EXISTS IN THE DB with this EXACT title
    movies_found = search_title(title, 0)
    if len(movies_found) >= 1:  # if the DB has 1 or more entries found
        selected_movie = show_found_movies_and_select(movies_found)
        if len(selected_movie) == 0:  # User pressed ENTER to escape
            print("The user aborted deletion!")
            return tuple()
        # The user selected the movie
        print(f"Movie {selected_movie} was selected. ")
        return selected_movie
    # No movies found. Searching for movies with similar name
    print("Movie not found. Searching for movies with similar name")
    movies_found = search_title(title, 3)
    if len(movies_found) > 0:  # If 1 or more similar movies found
        print(
            BColors.ENDC +
            "Found 1 or more movies with a similar name, please select")
        selected_movie = show_found_movies_and_select(movies_found)
        print(selected_movie)
        if len(selected_movie) != 0:  # The user selected a movie
            return selected_movie
        # No movies with similar names found
        print(BColors.ENDC + "No movie found with that name in the DB")
        return tuple()
    # if No movie found:
    print("Movie not found in the DB, nor movies with a similar name")
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
    print("This is the movie selected: ", selected_movie)
    print("Type: ", type(selected_movie))
    if len(selected_movie) == 0:
        return False
    if mss.delete_movie(
            selected_movie[0],
            selected_movie[2], current_user_id):  # check if the deletion was successful
        print(f"Movie {selected_movie[2]} deleted successfully.")
        return True
    # If deletion was not successful
    print(f"Deleting movie {selected_movie[2]} failed...")
    return False

# updates a movie from the dict. Returns the updated movie name or empty
# string if it failed


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
    pass
    # selected_movie = select_movie_id()
    # print(selected_movie)
    # if len(selected_movie) == 0:
    #     return False
    # new_rating = enter_rating()
    # print(selected_movie)
    #
    # if mss.update_movie(
    #         selected_movie[0],
    #         new_rating,
    #         selected_movie[1]):  # check if the deletion was successful
    #     print(
    #         f"Movie {
    #             selected_movie[1]} with ID{
    #             selected_movie[0]} updated successfully.")
    #     return True
    # # If deletion was not successful
    # print(f"Deleting of movie {selected_movie[1]} failed...")
    # return False


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

    print(BColors.ENDC)
    rating_list = []
    movies = mss.list_all_movies()
    for movie in movies:
        rating_list.append(movie[4])
    print(f"rating_list: {rating_list}")
    average_rating = statistics.mean(rating_list)
    median_rating = statistics.median(rating_list)
    best, max_rat, worst, min_rat = max_min_worst_best_movie(movies, rating_list)
    print(BColors.ENDC + f"Showing you now the statistics of all movies in the DB")
    print(f"Average imdbRating: {average_rating}")
    print(f"Median imdbRating: {median_rating}")
    print(f"Best movie: {best}, {max_rat}")
    print(f"Worst movie: {worst}, {min_rat}")


def command_random_movie() -> tuple:
    """
    selects a random movie and returns a tuple including the movie title and it's imdbRating
    """
    # Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    movies = mss.list_all_movies()
    random_movie = random.choice(movies)
    print(
        BColors.ENDC +
        f"Your movie for tonight: {
            random_movie[2]}, it's rated {
            random_movie[4]}.")
    return random_movie


def editing_distance(search_string: str, movie_title: str) -> int:
    """ NOT YET READY FOR MATCH_TYPE 4
    This function calculates the distance between the search_string and movie title
    and returns the "distance" between these 2 strings. The distance is calculated
    using fuzzy matching, using the "thefuzz" library

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
                BColors.FAIL +
                "search function does not exist with that match_type")
        movies_found = list(mss.search_movie(search_string, current_user_id, match_type))
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


def command_sort_by_rating(direction: str = 'descending') -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
    the function returns the sorted list ascending or descending, based upon input
    parameter 'direction'
    :param movies
    :param match_type:
    :return:
    """
    movie_list = mss.list_movies(current_user_id)
    if direction == 'descending':
        descending = True
    else:
        descending = False
    # sorts the list of tuples based on the imdbRating (tup[4])
    sorted_list = sorted(
        movie_list,
        key=lambda tup: tup[4], reverse=descending)
    print(BColors.ENDC + f"Showing you now all movies in the DB for {current_username} sorted by rating in {direction}")
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
    print(BColors.ENDC + "File histogram.png is created")


def command_generate_webstie():
    wg.generate_website(mss.list_movies(current_user_id),current_username)

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
        print(f"User profile for {username} created successfully.")
        return user_id, username
    else:
        print(f"Failed to create user profile for {username}. Exiting application.")
        return -1, ""

def command_update_user_profile():
    """
    updates the user profile in the database by asking for the username and email address
    :return:
    """
    global current_user_id, current_username
    clear_screen()
    command_list_users()
    selected_user_id = input("Enter the ID of the user you want to update or press ENTER to abort: ")
    if selected_user_id == "":
        print("User profile update aborted.")
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
            print("Invalid user ID provided. User profile update aborted.")
            return
    except (ValueError, TypeError):
        print("Invalid input provided. User profile update aborted.")
        return
    username = input(f"Enter a new username (was {orig_username}): ")
    if username == "":
        username = orig_username
        print("Using original username: ", username)
    email_address = input(f"Enter a new email address (was {orig_email_address}): ")
    if email_address == "":
        email_address = orig_email_address
        print("Using original email address: ", email_address)
    if uss.update_user_profile(selected_user_id,username, email_address):
        print(f"User profile for {username} updated successfully for user {selected_user_id}.")
        if current_user_id == selected_user_id:
            current_username = username
    else:
        print(f"Failed to update user profile for {current_user_id}.")
        
def command_select_user() -> tuple:
    """
    Asks the user to select a user profile from the database. Returns the user_id of the selected user.
    If no users are available, it will ask to create a new user profile. 
    if users are available, it will show the list of users and ask to select one by providing the user_id.
    if the user provides an invalid user_id, it will ask again until a valid user_id is provided or the user presses ENTER to abort.
    if the user presses ENTER to abort, it will return None.
    If the user selects to create a new user profile, it will ask for the username and email address and create a new user profile in the database.

    :return: user_id of the selected user or None if no user is selected
    """
    global current_user_id, current_username
    users = uss.list_users()
    if not users:
        print("No users found in the database. Please create a new user profile.")
        user_id, username = create_new_user()
        if user_id != -1:
            print(f"User profile for {username} created successfully.")
            return user_id, username
        else:
            print(f"Failed to create user profile for {username}. Exiting application.")
            return -1, ""
    else:
        print("Available users:")
        for user in users:
            print(f"{user[0]} - {user[1]}: ({user[2]})")
        while True:
            try:
                selected_user_id = input("Enter the ID of the user you want to select or type 'new' to create a new profile: ")
                if selected_user_id.lower() == 'new':
                    user_id, username = create_new_user()
                    return user_id, username
                selected_user_id = int(selected_user_id)
                for user in users:
                    if user[0] == selected_user_id:
                        current_user_id = selected_user_id
                        current_username = user[1]  
                        return selected_user_id, user[1]
                print("Invalid user ID. Please try again.")
            except (ValueError, TypeError):
                print("Please enter a valid integer for the user ID.")

def command_list_users():
    """
    Lists all the users in the database by showing their user_id, username and email address.
    :return:
    """
    users = uss.list_users()
    if not users:
        print("No users found in the database.")
    else:
        print("Available users:")
        for user in users:
            print(f"{user[0]} - {user[1]}: ({user[2]})")

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

    global current_user_id, current_username
    users = uss.list_users()
    if not users:
        print("No users found in the database.")
        return
    print("Available users:")
    for user in users:
        print(f"{user[0]} - {user[1]}: ({user[2]})")
    while True:
        try:
            selected_user_id = input("Enter the ID of the user you want to delete or press ENTER to abort: ")
            if selected_user_id == "":
                print("User deletion aborted.")
                return
            selected_user_id = int(selected_user_id)
            for user in users:
                if user[0] == selected_user_id:
                    if uss.delete_user(selected_user_id):
                        delete_all_movies_of_user(selected_user_id)
                        print(f"User {user[1]} and all associated movies deleted successfully.")
                        if current_user_id == selected_user_id:
                            current_user_id = -1
                            current_username = ""
                            command_select_user()
                        print(f"User {user[1]} deleted successfully.")
                    else:
                        print(f"Failed to delete user {user[1]}.")
                    return
            print("Invalid user ID. Please try again.")
        except (ValueError, TypeError):
            print("Please enter a valid integer for the user ID.")
    


# pylint: disable=pointless-string-statement
"""
Function Dispatch Dictionary
"""
FUNCTIONS = {1: (command_list_movies, "List all my movies"),
             2: (command_list_all_movies, "List all movies in the database"),
             3: (command_add_movie, "Add movie"),
             4: (command_delete_movie, "Delete movie"),
             5: (command_show_stats, "Show movie statistics"),
             6: (command_random_movie, "Select a movie randomly"),
             7: (command_search_movie, "Search by title"),
             8: (command_sort_by_rating, "Movies sorted by rating"),
             9: (command_create_rating_histogram, "Create rating histogram"),
             10: (command_generate_webstie, "Generate the website"),
             11: (command_update_user_profile, "Update user profile"),
             12: (command_select_user, "Change user"),
             13: (command_create_new_user, "Add user"),
             14: (command_list_users, "List users"),
             15: (command_delete_user, "Delete user"),
             0: (command_quit, "Exit")
             }


def main():
    """
    Order of the display of the menu and ask for user input to select an option
    :return:
    """
    clear_screen()
    global current_user_id, current_username
    selected_user_id, selected_username = command_select_user() # ask the user to select a user profile, returns the user_id of the selected user
    current_user_id = selected_user_id
    current_username = selected_username
    print(f"Selected user ID: {current_user_id}, username: {current_username}")

    if selected_user_id is None:
        print("No user selected, exiting the application.")
        return
    while True:
        menu_selection = show_menu()
        menu_selection()
        input(BColors.OKBLUE + "\nPress enter to continue")


if __name__ == "__main__":
    main()
