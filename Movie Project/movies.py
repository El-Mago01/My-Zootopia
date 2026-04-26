# File revision information: PA3
import os
import statistics
import random
import sys
from random import choice
from time import time

import matplotlib
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

def command_list_movies():
    """
    list the all available movies in the current DB
    """
    movies=mss.list_movies()
    print(movies)
    print(bcolors.ENDC + f"{'imdbID':<12}|{'Title':<80}|{'Year':<6}|{'imdbRating':<8}|{'Poster link':<2}")
    print("============================================================================================"
          "============================================================================================")
    for movie in movies:
        print(bcolors.ENDC+ f"{movie[0]:<12}|{movie[1]:<80}|{movie[2]:<6}|{movie[3]:<8}|{movie[4]:<2}")

def enter_rating()->float:
    while True:
        try:
            rating = input("Enter movie imdbRating: ").strip()
            if rating == "":
                return -1
            rating = float(rating)
            if (0 <= rating <= 10):
                return rating
            else:
                raise ValueError
        except (TypeError, ValueError):
            print(bcolors.FAIL + 'Please enter a valid imdbRating value from 0-10 or Enter to abort' + bcolors.ENDC)

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
    def select_movie_with_id(imdbID, movies_found)->dict:
        movie={}
        for movie in movies_found:
            if imdbID == movie['imdbID']:
                return movie
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
        print(f"Showing you now {len(movies_found)} movies")
        print(f"{'imdbID':<15}  - {'Title':<40} - {'Year':<10}")
        print("==============================================================")
        for movie in movies_found:
            print(f"{movie['imdbID']:<15}  - {movie['Title']:<40} - {movie['Year']:<10}")
        while 1:
            imdbID = input(bcolors.OKGREEN + "Enter movie valid imdbID or ENTER to abort: ").strip()

            if imdbID == "":
                break
            selected_movie = select_movie_with_id(imdbID,movies_found)
            if len(selected_movie) != 0: # If a valid imdbID was provided
                break
            else:
                print(bcolors.FAIL + "Please enter a valid movie imdbID or ENTER to abort" + bcolors.ENDC)
        if imdbID != "": # User provided a valid imdbID
            try:
                year = int(mdf.fetch_specific_movie_detail_item('Year', imdbID))
            except ValueError:
                year = 0
            try:
                rating = float(mdf.fetch_specific_movie_detail_item('imdbRating', imdbID))
            except ValueError:
                rating = 0
            print(selected_movie)
            movie={'imdbID': imdbID,
                   'Title': selected_movie['Title'],
                   'Year': year,
                   'imdbRating': rating,
                   'Poster': selected_movie['Poster']}
            return movie
        else: # User pressed ENTER to abort
            return {}

    def add_the_movie(movie: dict) -> None:
        try:
            mss.add_movie(movie)
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
                print("The following similar movies already exist in the DB:")
                print(bcolors.ENDC + f"{'ID':<8}| {'Title':<80}| {'Year':<10}")
                print("================================================================================================")
                for movie in movies_found:
                    print(bcolors.ENDC + f"ID{movie[0]:<8}| {movie[1]:<80}| {movie[2]:<10}")
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

    def show_found_movies_and_select(movies: list) -> int:
        print("=======================================================================================================")
        print(bcolors.ENDC + f"{'imdbID':<12}|{'Title':<80}|{'Year':<6}|{'imdbRating':<6}")
        for movie in movies:
            print(bcolors.ENDC + f"{movie[0]:<12}|{movie[1]:<80}|{movie[2]:<6}|{movie[3]:<6}")
        valid_entry=False
        movie_choice = -1
        while valid_entry == False:
            imdbID = input(
            f"what movie do you want to select the imdbID to delete? "
            f"Or press Enter to return to MENU: ")
            if len(imdbID) == 0:
                movie_choice = -1
                break
            counter=0
            for movie in movies:
                if movie[0] == imdbID:
                    valid_entry = True
                    movie_choice = counter
                    break
                counter+=1

        print ("movie choice =", movie_choice)
        return movie_choice

    # =======================================================================
    # The actual start of function select_movie_id
    # =======================================================================
    title=enter_movie_title()
    # CHECK IF A MOVIE WITH THIS TITLE EXISTS IN THE DB with this EXACT title
    movies_found=search_title(title,0)
    if len(movies_found) >= 1: # if the DB has 1 or more entries found
        user_choice = show_found_movies_and_select(movies_found)
        if user_choice == -1:  # User did not select a movie to delete
            print("Deletion of movie aborted!")
            return tuple()
        else:  # The user selected the movie to delete
            print(f"Movie {movies_found[user_choice][1]} found. ")
            return movies_found[user_choice]
    else:  # No movies found. Searching for movies with similar name
        print("Movie not found. Searching for movies with similar name")
        movies_found = search_title(title, 3)
        if len(movies_found) > 0:  # If 1 or more similar movies found
            print(bcolors.ENDC+"Found 1 or more movies with a similar name, please select")
            user_choice = show_found_movies_and_select(movies_found)
            print(user_choice)
            if user_choice != -1: # User aborted the search by pressing ENTER
                return movies_found[user_choice]
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
    if mss.delete_movie(selected_movie[0],selected_movie[1]):  # check if the deletion was successful
        print(f"Movie {selected_movie[1]} deleted successfully.")
        return True
    else:  # If deletion was not successful
        print(f"Deleting of movie {selected_movie[1]} failed...")
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

def max_min_rating_movie() -> tuple:
    """
    Gather the statistics from the films and imdbRating in the dict.
    Return best movie, worst movie, and the related imdbRating as tuple
    """
    min_rating = min(movies.values())
    max_rating = max(movies.values())
    worst_movie = ""
    best_movie = ""
    for movie in movies:
        if movies[movie] == min_rating:
            worst_movie+=movie + " + " # in case 2 movies have the worst imdbRating
        if movies[movie] == max_rating:
            best_movie+=movie + " + " # in case 2 movies have the best imdbRating
    if best_movie == "":
        best_movie = "Not found + "
    if worst_movie == "":
        worst_movie = "Not found + "
    return best_movie[0:-3],max_rating, worst_movie[0:-3], min_rating # slicing to remove the + at the end

def show_stats():

    print(bcolors.ENDC)
    average_rating=statistics.mean(movies.values())
    median_rating=statistics.median(list(movies.values()))
    best,max_rat, worst, min_rat = max_min_rating_movie(movies)
    print(f"Average imdbRating: {average_rating}")
    print(f"Median imdbRating: {median_rating}")
    print(f"Best movie: {best}, {max_rat}")
    print(f"Worst movie: {worst}, {min_rat}")

def select_random_movie() -> tuple:
    """
    selects a random movie and returns a tuple including the movie title and it's imdbRating
    """
    #Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    random_movie=random.choice(list(movies.keys()))
    print(bcolors.ENDC + f"Your movie for tonight: {random_movie}, it's rated {movies[random_movie]}")
    return random_movie, movies[random_movie]

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

def sort_by_rating(direction:str='descending') -> list:
    """
    orders the list using the "sorted" function with one-liner function for key
    the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
    the function returns the sorted list ascending or descending, based upon input parameter 'direction'
    :param movies
    :param match_type:
    :return:
    """
    movie_list=movies.items()
    if direction == 'descending':
        descending=True
    else:
        descending=False
    sorted_list = sorted(movie_list, key=lambda tup: tup[1],
                         reverse=descending)  # sorts the list of tuples based on the imdbRating (tup[1])
    print()
    for movie,imdbRating in sorted_list:
        print(bcolors.ENDC + f"{movie}: {imdbRating}")
    return sorted_list


def create_rating_histogram(movies:dict):
    """
    Creates a histogram of the ratings in the dict
    uses the following imports:
    import numpy as np
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    """
    a=list(movies.values())
    fig=plt.hist(a)
    plt.title("Histogram of movie imdbRatings")
    plt.xlabel("value")
    plt.ylabel("frequency")
    plt.show
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
              5: (show_stats, "Show movie statistics"),
              6: (select_random_movie, "Select a movie randomly"),
              7: (search_title, "Search by title"),
              8: (sort_by_rating, "Movies sorted by rating"),
              9: (create_rating_histogram, "Create rating histogram")
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
