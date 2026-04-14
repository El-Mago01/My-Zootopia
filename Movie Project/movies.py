import os
import statistics
import random
import sys
import matplotlib
import numpy as np
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thefuzz import fuzz

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

# Clean the screen before showing the menu. Does not seem to work well though on this terminal
def clear_screen():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system('clear')

#Check if the content of the string is a float
def is_float(string:str) -> bool:
    try:
        float(string)
    except ValueError:
        return False
    return True

# Show the menu based on the menu_string and ask for input. Only allow valid input.
def show_menu():
    menu_string = ("** ** ** ** ** My Movies Database ** ** ** ** ** \n\n"
                   "Menu: \n"
                   "1. List movies\n"
                   "2. Add movie\n"
                   "3. Delete movie\n"
                   "4. Update movie\n"
                   "5. Stats\n"
                   "6. Random movie\n"
                   "7. Search movie\n"
                   "8. Movies sorted by rating\n"
                   "9. Create rating histogram\n"
                   )
    correct_input_provided = False
    while correct_input_provided is False:
        clear_screen() # clears the screen
        print(bcolors.OKBLUE + menu_string)
        input_selection=input(bcolors.OKBLUE + "Enter choice(1 - 9): ")
        if input_selection.isnumeric() and (1 <= int(input_selection) <= 9):
            correct_input_provided = True
            input_selection=int(input_selection)
        if correct_input_provided == False:
            input(bcolors.FAIL + "Input should be between 1-9. Press enter to continue")
    return input_selection

# list the available movies in the current dict
def list_movies(movies:dict):
    print(bcolors.ENDC + f"{len(movies)} movies in total")
    for movie in movies:
        print(f"{movie}: {movies[movie]}")

# The current movie list contains a name (string) and a rating (a float)
# This function ensures valid user input for name and rating
def get_correct_movie_input() -> tuple:
    correct_input_provided = False
    while correct_input_provided is False:
        movie = input(bcolors.OKGREEN + "Enter movie name: ")
        rating = input("Enter new movie rating: ")
        if is_float(rating):
            if 0<= float(rating) <=10:
                correct_input_provided = True
                rating=float(rating)

        if correct_input_provided == False:
            input(bcolors.FAIL + "Input provide valid input. Press enter to continue!" + bcolors.ENDC)
    return movie, rating, correct_input_provided

# Adds a movie to the dict. Returns a boolean indicating success or not
def add_movie(movies:dict) -> bool:
    movie, rating, correct_input_provided=get_correct_movie_input()
    if not correct_input_provided: # if correct input was provided (this should always be True
        print("Movie can not be added, wrong input")
        return False
    found_movies=search_movies(movies,movie,1)
    if len(search_movies(movies,movie,1))>0 :#search case-insensitive, but matching characters
        print(f"Movie {movie} is already stored")
        return False

    movies[movie] = float(rating)
    print(f"Movie {movie} successfully added")
    return True

# deletes a movie from the dict. Returns a boolean indicating success or not
def delete_movie(movies:dict, movie_to_delete:str) -> bool:
    try:
        movies.pop(movie_to_delete)
    except:
        print(bcolors.FAIL + f"Movie {movie_to_delete} doesn't exist!" + bcolors.ENDC)
        return False
    return True

# updates a movie from the dict. Returns the updated movie name or empty string if it failed
def update_movie(movies:dict) -> str:
    movie_to_update, new_rating, correct_input_provided = get_correct_movie_input()
    movies_found=search_movies(movies,movie_to_update,2)
    if len(movies_found) > 0: # in case there is an exact match already
        movies.update({movie_to_update: new_rating})
        return movie_to_update
    else:
        return ""

# gather the statistics from the films and ratings in the dict.
# best movie, worst movie, and the related ratings as tuple
def max_min_rating_movie(movies: dict) -> tuple:
    min_rating = min(movies.values())
    max_rating = max(movies.values())
    worst_movie = ""
    best_movie = ""
    for movie in movies:
        if movies[movie] == min_rating:
            worst_movie+=movie + " + " # in case 2 movies have the worst rating
        if movies[movie] == max_rating:
            best_movie+=movie + " + " # in case 2 movies have the best rating
    if best_movie == "":
        best_movie = "Not found + "
    if worst_movie == "":
        worst_movie = "Not found + "
    return best_movie[0:-3],max_rating, worst_movie[0:-3], min_rating # slicing to remove the + at the end

# prints the statistics from the movie dictionary. No return value
def show_stats(movies:dict):
    print(bcolors.ENDC)
    average_rating=sum(movies.values())/len(movies)
    median_rating=statistics.median(list(movies.values()))
    best,max_rat, worst, min_rat = max_min_rating_movie(movies)
    print(f"Average rating: {average_rating}")
    print(f"Median rating: {median_rating}")
    print(f"Best movie: {best}, {max_rat}")
    print(f"Worst movie: {worst}, {min_rat}")

# selects a random movie and returns a tuple including the movie title and it's rating
def select_random_movie(movies:dict) -> tuple:
    #Your movie for tonight: Star Wars: Episode V, it's rated 8.7
    random_movie=random.choice(list(movies.keys()))
    print(bcolors.ENDC + f"Your movie for tonight: {random_movie}, it's rated {movies[random_movie]}")
    return random_movie, movies[random_movie]

# pretty prints the output of the search. No return value
def pretty_print(found_movies:dict,search_string):
    max_distance = 0
    for movie in found_movies:
        if max_distance < found_movies[movie][1]:
            max_distance = found_movies[movie][1]
    if max_distance > 95:
        for movie in found_movies:
            if found_movies[movie][1] == max_distance:
                print(bcolors.ENDC + f"{movie}, {found_movies[movie][0]}")
        if len(found_movies) > 1:
            print(bcolors.WARNING + "These movies might also fit your search:")
            for movie in found_movies:
                if found_movies[movie][1] < max_distance:
                    print(bcolors.ENDC +f"{movie}, with rating {found_movies[movie][0]}?")
            print(bcolors.ENDC)
    elif len(found_movies) > 0:
        print(bcolors.WARNING + f"The movie {search_string} does not exist. Did you mean:" + bcolors.ENDC)
        for movie in found_movies:
            print(f"{movie}, with rating {found_movies[movie][0]}?")
    else:
        print(bcolors.FAIL + "Movie not found" + bcolors.ENDC)

# This function calculates the distance between the search_string and movie title and returns the "distance"
# between these 2 strings. The distance is calculated using fuzzy matching, using the "thefuzz" library
def editing_distance(search_string:str, movie_title:str) ->int:
    distance=fuzz.ratio(search_string,movie_title)
    # print (distance)
    return distance
# searches for movies in the dict using the search_string and 4 variants expressed by match_type (int)
#   match_type 0 => not exact & case-insensitive
#   match_type 1 => matching characters, but case-insensitive
#   match_type 2 => exact match, and case-sensitive
#   match_type 3 => fuzzy matching
def search_movies(movies:dict, search_string, match_type:int=0) -> dict:
    e_distance=0 # the fuzzy matching distance is initially set to 0,
                 # i.e. there is nothing in common with search string

    movies_found ={} # create an empty dict to be used by all the found movies

    if match_type >3 or match_type<0: # needs to be updated later to ensure proper error handling.
        print(bcolors.FAIL + "Coding error, match_type var out of bound. Value {match_type}" + bcolors.ENDC)
        movies_found={'Fault message': 'Coding Error'}
        return movies_found
    movies_names = movies.keys()
    for movie in movies_names:
        if ((search_string.lower() in movie.lower() and match_type == 0) or
                (search_string.lower() == movie.lower() and match_type == 1) or
                (search_string == movie and match_type == 2) or
                (editing_distance(search_string,movie) > FUZZY_SENS and match_type == 3)):
            e_distance=editing_distance(search_string, movie)
            movies_found[movie]=(movies[movie],e_distance)
    return movies_found

# converts the dict to a list including the rating and movie title
# orders the list using the "sorted" function with one-liner function for key
# the anonymous one-liner function key=lambda tup: tup[1] ensures the sorting on rating
# the function returns the sorted list ascending or descending, based upon input parameter 'direction'
def sort_by_rating(movies:dict, direction:str='descending') -> list:
    movie_list=movies.items()
    if direction == 'descending':
        descending=True
    else:
        descending=False
    sorted_list = sorted(movie_list, key=lambda tup: tup[1],
                         reverse=descending)  # sorts the list of tuples based on the rating (tup[1])
    print()
    for movie,rating in sorted_list:
        print(bcolors.ENDC + f"{movie}: {rating}")
    return sorted_list

# creates a histogram of the ratings in the dict
# # uses the following imports:
# import numpy as np
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

def create_rating_histogram(movies:dict):
    a=list(movies.values())
    fig=plt.hist(a)
    plt.title("Histogram of movie ratings")
    plt.xlabel("value")
    plt.ylabel("frequency")
    plt.show
    plt.savefig("histogram.png")
    sys.stdout.flush()
    print(bcolors.ENDC + "File histogram.png is created")

# In main() the movies initial library is constructed and the menu is displayed.
# based upon the selected menu-item by user, the right function is called.
def main():
    # Dictionary to store the movies and the rating
    movies = {
        "The Shawshank Redemption": 9.5,
        "Pulp Fiction": 8.8,
        "The Room": 3.6,
        "The Godfather": 9.2,
        "The Godfather: Part II": 9.0,
        "The Dark Knight": 9.0,
        "12 Angry Men": 8.9,
        "Everything Everywhere All At Once": 8.9,
        "Forrest Gump": 8.8,
        "Star Wars: Episode V": 8.7
    }
    no_interrupt=True
    while no_interrupt:
        menu_selection=show_menu()
        if menu_selection == 1:
            list_movies(movies)
        if menu_selection == 2:
            add_movie(movies)
        if menu_selection == 3:
            movie_to_delete = input("Enter movie name to delete: ")
            if delete_movie(movies,movie_to_delete):
                print(f"Movie {movie_to_delete} successfully deleted")
        if menu_selection == 4:
            updated_movie=update_movie((movies))
            if len(updated_movie) > 0:
                print(f"Movie {updated_movie} successfully updated")
            else:
                print(bcolors.FAIL +f"Movie doesn't exist!" + bcolors.ENDC)
        if menu_selection == 5:
            show_stats(movies)
        if menu_selection == 6:
            select_random_movie(movies)
        if menu_selection == 7:
            search_string = input("\nEnter part of movie name:")
            found_movies = search_movies(movies, search_string, 3)
            # if len(found_movies) == 0:
            #     print("film not found ")
            pretty_print(found_movies,search_string)
        if menu_selection == 8:
            sort_by_rating(movies)

        if menu_selection == 9:
            create_rating_histogram(movies)
        input(bcolors.OKBLUE + "\nPress enter to continue")

if __name__ == "__main__":
    main()
