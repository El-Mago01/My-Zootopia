# File revision information: PA3
import os
import sqlite3
import statistics
import random
import sys
from random import choice
from time import time

import matplotlib
import sqlalchemy

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thefuzz import fuzz
import movie_storage_sql as mss
import movie_detail_fetcher as mdf

# Algorithm:
# =============================
# step 10: show the menu numbered from 1-8 and ask for input
# step 20: check that the provided input is a number from 1-8, if not, clear the screen and show the menu again.
# step 30: execute the desired CRUD function or analysis function
# step 40: show the results to screen
# step 50: ask for an enter to continue
# step 60: after enter is provided, start from 10 again.

# class bcolors used for color setting of output text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Constant used for the fuzzy search sensitivity. Adjust to higher level to focus the search quality
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

#Check if the content of the string is a float
def is_float(string:str) -> bool:
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
        print(bcolors.OKBLUE + "** ** ** ** ** My Movies Database ** ** ** ** ** \n\n")
        for key in FUNCTIONS:
            print(bcolors.OKBLUE + f"{key} - {FUNCTIONS[key][1]}" + bcolors.ENDC)
        try:
            user_choice=int(input(bcolors.OKBLUE + "Enter choice(1 - 9): "))
            print(user_choice)
            if user_choice in FUNCTIONS:
                print("returning", FUNCTIONS[user_choice][0])
                return FUNCTIONS[user_choice][0]
        except (TypeError, ValueError):
            print(bcolors.FAIL + "Please enter a valid choice!" + bcolors.ENDC)

def command_list_movies(movie_list:list=[]):
    """
    list the all available movies in the current DB or list the provided movies
    """
    if len(movie_list)==0: #no list with movies is provided, so fetch the ones from the DB
        movie_list=mss.list_movies()
        print(bcolors.ENDC + f"Showing you now {len(movie_list)} movie(s)")
        print(bcolors.ENDC + f"{'ID':<5}|{'imdbID':<12}|{'Title':<80}|{'Year':<6}|{'imdbRating':<12}|{'Poster link':<2}")
        print("============================================================================================"
              "============================================================================================")
        for movie in movie_list:
            print(bcolors.ENDC + f"{movie[0]:<5}|{movie[1]:<12}|{movie[2]:<80}|"
                                 f"{movie[3]:<6}|{movie[4]:<12}|{movie[5]:<2}")
    else:
        try:
            print(bcolors.ENDC + f"Showing you now {len(movie_list)} movie(s)")
            print(bcolors.ENDC + f"{'ID':<5}|{'imdbID':<12}|{'Title':<80}|{'Year':<6}|{'imdbRating':<12}|{'Poster link':<2}")
            print("============================================================================================"
                  "============================================================================================")
            if type(movie_list[0]) is tuple or type(movie_list[0]) is sqlalchemy.engine.row.Row:
                for movie in movie_list:
                    print(bcolors.ENDC + f"{movie[0]:<5}|{movie[1]:<12}|{movie[2]:<80}|"
                                         f"{movie[3]:<6}|{movie[4]:<12}|{movie[5]:<2}")
            elif type(movie_list[0]) is dict:
                counter=1
                for movie in movie_list:
                    print(bcolors.ENDC + f"{counter:<5}|{movie['imdbID']:<12}|{movie['Title']:<80}|"
                                         f"{movie['Year']:<6}|{'-':<12}|{movie['Poster']:<2}|")
                    counter += 1
            else:
                raise TypeError("Unexpected Type", type(movie_list[0]))
        except (TypeError,KeyError) as e:
            print("Could not print the list of movies! Due to: ",e)
            print("going for a simple print instead")
            for movie in movie_list:
                print(movie)
                print(type(movie))

def enter_rating()->float:
    while True:
        try:
            rating = input("Enter movie rating: ").strip()
            if rating == "":
                return -1
            rating = float(rating)
            if (0 <= rating <= 10):
                return rating
            else:
                raise ValueError
        except (TypeError, ValueError):
            print(bcolors.FAIL + 'Please enter a valid rating value from 0-10 or Enter to abort' + bcolors.ENDC)

def enter_year()->int:
    while True:
        try:
            year = input(bcolors.OKGREEN + "Enter the year: ").strip()
            if year == "":
                return -1
            year = int(year)
            if year > 1888:
                return year
            else:
                raise ValueError
        except (TypeError, ValueError):
            print(bcolors.FAIL + "Please enter a valid year as a number of 4 digits, from 1888 onwards" + bcolors.ENDC)
            input(bcolors.FAIL + "Press enter to continue!" + bcolors.ENDC)

def enter_movie_title():
    while 1:
        title = input(bcolors.OKGREEN + "Enter movie title: ").strip()
        if (len(title) >= 2): # Assuming there is no movie title with less than 2 characters.
            return title
        else:
            print(bcolors.FAIL + "Please enter a valid movie title of at least 3 characters"+ bcolors.ENDC)


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
    def select_movie_with_id(movie_id, movies_found)->dict:
        print(f"{movie_id}These were the movies found:, {movies_found}")
        print(type(movies_found))
        if movie_id <= len(movies_found)-1: # id is the index in the movies_found list.
            print(f"This is the selected movie under id {movie_id}: \n{movies_found[movie_id]}")
            return movies_found[movie_id]
        return {}

    def enter_correct_movie_input() -> dict:
        """
        algorithm:
        1. Ask input for movie title.
        2. Check if the input is not empty, at least 1 character
        3. Find all movies containing the movie title
        4. Print all the found movies, including the imdbID, title and year
        5. Ask the user to enter the movie it wanted to insert
        6. For the provided imdbID, return the full title, the year and, if available, an imdbRating.

        :return: full title, the year and, if available, an imdbRating.
        """
        title = enter_movie_title()
        selected_movie={}
        movies_found=mdf.fetch_movie_general_data(title)
        if len(movies_found) == 0:
            return {}
        command_list_movies(movies_found)
        while 1:
            selected_id = input(bcolors.OKGREEN + "Enter movie valid ID or ENTER to abort: ").strip()
            if selected_id == "":
                break
            try:
                selected_id=int(selected_id)
                print(selected_id)
                selected_movie = select_movie_with_id(selected_id-1, movies_found)
                if len(selected_movie) != 0:  # If a valid id was provided
                    break
            except ValueError:
                pass
            print(bcolors.FAIL + "Please enter a valid movie id as number or press ENTER to abort" + bcolors.ENDC)

        if selected_id != "": # User provided a valid imdbID
            try:
                year = int(mdf.fetch_specific_movie_detail_item('Year', selected_movie['imdbID']))
            except ValueError:
                year = 0
            try:
                rating = float(mdf.fetch_specific_movie_detail_item('imdbRating', selected_movie['imdbID']))
            except ValueError:
                rating = 0
            print(selected_movie)
            movie={'imdbID': selected_movie['imdbID'],
                   'Title': selected_movie['Title'],
                   'Year': year,
                   'Rating': rating,
                   'Poster': selected_movie['Poster']}
            return movie
        else: # User pressed ENTER to abort
            return {}

    def add_the_movie(movie: dict) -> None:
        print("Storing the movie")
        try:
            if not mss.add_movie(movie):
                raise sqlite3.IntegrityError("Movie could not be stored. UNIQUE constraint failed!")
        except Exception as error:
            print(f"Movie {movie['Title']} not stored successfully. Please contact your system administrator")
            print("Fault message is: ", error)
        print(f"Movie {movie['Title']} successfully added")

    new_movie = enter_correct_movie_input()
    if len(new_movie) != 0: # A valid imdbID was provided
        if len(new_movie['Title']) != 0:
            movies_found=search_title(new_movie['Title'],3)
            if len(movies_found) == 0:
                add_the_movie(new_movie)
            else:
                print(bcolors.ENDC + "The following similar movies already exist in the DB:")
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
        valid_entry=False
        while valid_entry == False:
            try:
                id = input(
                f"Please provide ID of the movie you would like to select? "
                f"Or press Enter to return to MENU: ")
                if len(id) == 0:
                    return tuple()
                for movie in movies:
                    if movie[0] == int(id):
                        valid_entry = True
                        print("Selected movie =", movie)
                        return movie
            except (ValueError,TypeError):
                pass
            print(bcolors.WARNING + "Wrong input provided, please try again" + bcolors.ENDC)



    # =======================================================================
    # The actual start of function select_movie_id
    # =======================================================================
    title=enter_movie_title()
    # CHECK IF A MOVIE WITH THIS TITLE EXISTS IN THE DB with this EXACT title
    movies_found=search_title(title,0)
    if len(movies_found) >= 1: # if the DB has 1 or more entries found
        selected_movie = show_found_movies_and_select(movies_found)
        if len(selected_movie) == 0:  # User pressed ENTER to escape
            print("The user aborted deletion!")
            return tuple()
        else:  # The user selected the movie
            print(f"Movie {selected_movie} was selected. ")
            return selected_movie
    else:  # No movies found. Searching for movies with similar name
        print("Movie not found. Searching for movies with similar name")
        movies_found = search_title(title, 3)
        if len(movies_found) > 0:  # If 1 or more similar movies found
            print(bcolors.ENDC+"Found 1 or more movies with a similar name, please select")
            selected_movie = show_found_movies_and_select(movies_found)
            print(selected_movie)
            if len(selected_movie) != 0: #The user selected a movie
                return selected_movie
            else: # No movies with similar names found
                print(bcolors.ENDC + "No movie found with that name in the DB")
                return tuple()
        else:
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
    selected_movie=select_movie_id()
    print("This is the movie selected: ",selected_movie)
    print("Type: ", type(selected_movie))
    if len(selected_movie) == 0:
        return False
    if mss.delete_movie(selected_movie[0],selected_movie[2]):  # check if the deletion was successful
        print(f"Movie {selected_movie[2]} deleted successfully.")
        return True
    else:  # If deletion was not successful
        print(f"Deleting of movie {selected_movie[2]} failed...")
        return False

# updates a movie from the dict. Returns the updated movie name or empty string if it failed
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
    selected_movie=select_movie_id()
    print(selected_movie)
    if len(selected_movie) == 0:
        return False
    new_rating=enter_rating()
    print(selected_movie)

    if mss.update_movie(selected_movie[0],new_rating,selected_movie[1]):  # check if the deletion was successful
        print(f"Movie {selected_movie[1]} with ID{selected_movie[0]} updated successfully.")
        return True
    else:  # If deletion was not successful
        print(f"Deleting of movie {selected_movie[1]} failed...")
        return False

def command_show_stats():
    def max_min_rating_movie(movies, rating_list) -> tuple:
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
                worst_movie += movie[2] + " + "  # in case 2 or more movies have the worst imdbRating
            if movie[4] == max_rating:
                best_movie += movie[2] + " + "  # in case 2 or more movies have the best imdbRating
        if best_movie == "":
            best_movie = "Not found + "
        if worst_movie == "":
            worst_movie = "Not found + "
        return best_movie[0:-3], max_rating, worst_movie[0:-3], min_rating  # slicing to remove the + at the end
    # =======================================================================
    # The actual start of function command_show_stats
    # =======================================================================

    print(bcolors.ENDC)
    rating_list=[]
    movies=mss.list_movies()
    for movie in movies:
        rating_list.append(movie[4])
    print(rating_list)
    average_rating=statistics.mean(rating_list)
    median_rating=statistics.median(rating_list)
    best,max_rat, worst, min_rat = max_min_rating_movie(movies, rating_list)
    print(f"Average imdbRating: {average_rating}")
    print(f"Median imdbRating: {median_rating}")
    print(f"Best movie: {best}, {max_rat}")
    print(f"Worst movie: {worst}, {min_rat}")

def command_random_movie() -> tuple:
    """
    selects a random movie and returns a tuple including the movie title and it's imdbRating
    """
    #Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    movies=mss.list_movies()
    random_movie=random.choice(movies)
    print(bcolors.ENDC + f"Your movie for tonight: {random_movie[2]}, it's rated {random_movie[4]}.")
    return random_movie

def editing_distance(search_string:str, movie_title:str) ->int:
    """ NOT YET READY FOR MATCH_TYPE 4
    This function calculates the distance between the search_string and movie title and returns the "distance"
    between these 2 strings. The distance is calculated using fuzzy matching, using the "thefuzz" library

    """
    distance=fuzz.ratio(search_string,movie_title)
    # print (distance)
    return distance

def search_title(search_string, match_type:int=0) -> list:
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

    movies_found =[] # create an empty dict to be used by all the found movies
    try:
        if match_type >3 or match_type<0:
            raise ReferenceError(bcolors.FAIL + "search function does not exist with that match_type")
        movies_found=list(mss.search_movie(search_string,match_type))
    except ReferenceError:
        print(bcolors.WARNING + "Movie not found" + bcolors.ENDC)

    return movies_found

def command_search_movie():
    title=enter_movie_title()
    movies_found=search_title(title,3)
    command_list_movies(movies_found)

def command_sort_by_rating(direction:str='descending') -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
    the function returns the sorted list ascending or descending, based upon input parameter 'direction'
    :param movies
    :param match_type:
    :return:
    """
    movie_list=mss.list_movies()
    if direction == 'descending':
        descending=True
    else:
        descending=False
    sorted_list = sorted(movie_list, key=lambda tup: tup[4],
                         reverse=descending)  # sorts the list of tuples based on the imdbRating (tup[4])
    command_list_movies(sorted_list)

def command_quit():
    exit()

def command_create_rating_histogram():
    """
    Creates a histogram of the ratings in the dict
    uses the following imports:
    import numpy as np
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    """
    movie_list=mss.list_movies()
    rating_list = []
    movies = mss.list_movies()
    for movie in movies:
        rating_list.append(movie[4])
    plt.hist(rating_list)
    plt.title("Histogram of movie imdbRatings")
    plt.xlabel("value")
    plt.ylabel("frequency")
    plt.show()
    plt.savefig("histogram.png")
    sys.stdout.flush()
    print(bcolors.ENDC + "File histogram.png is created")


"""
Function Dispatch Dictionary
"""
FUNCTIONS = { 1: (command_list_movies, "List movies"),
              2: (command_add_movie, "Add movie"),
              3: (command_delete_movie, "Delete movie"),
              # 4: (command_update_movie, "Update movie"),
              5: (command_show_stats, "Show movie statistics"),
              6: (command_random_movie, "Select a movie randomly"),
              7: (command_search_movie, "Search by title"),
              8: (command_sort_by_rating, "Movies sorted by rating"),
              9: (command_create_rating_histogram, "Create rating histogram"),
              0: (command_quit, "Exit")
}

def main():
    """
    Order of the display of the menu and ask for user input to select an option
    :return:
    """
    while True:
        menu_selection=show_menu()
        menu_selection()
        input(bcolors.OKBLUE + "\nPress enter to continue")

if __name__ == "__main__":
    main()
