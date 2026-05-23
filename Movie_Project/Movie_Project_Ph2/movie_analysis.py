"""
Movie Analysis Module
This module handles all the overall statistics related services
"""
import statistics
import sys
import matplotlib.pyplot as plt
from user_interface import Bcolors
import movie_storage as ms



def command_create_rating_histogram():
    """
    Creates a histogram of the ratings in the dict
    uses the following imports:
    import numpy as np
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    """
    rating_list = []
    movies = ms.fetch_all_movies()
    for movie in movies:
        rating_list.append(movie[4])
    plt.hist(rating_list)
    plt.title("Histogram of movie imdbRatings")
    plt.xlabel("value")
    plt.ylabel("frequency")
    plt.show()
    plt.savefig("histogram.png")
    sys.stdout.flush()
    print(Bcolors.LISTING + "File histogram.png is created")

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
            if movie[5] == min_rating:
                # in case 2 or more movies have the worst imdbRating
                worst_movie += movie[3] + " + "
            if movie[5] == max_rating:
                # in case 2 or more movies have the best imdbRating
                best_movie += movie[3] + " + "
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
    movies = ms.fetch_all_movies()
    for movie in movies:
        rating_list.append(movie[5])
    # print(Bcolors.LISTING + f"Rating_list: {rating_list}" + Bcolors.ENDC)
    average_rating = statistics.mean(rating_list)
    median_rating = statistics.median(rating_list)
    best, max_rat, worst, min_rat = max_min_worst_best_movie(movies, rating_list)
    print(
        Bcolors.LISTING
        + "Showing you now the statistics of all movies in the DB"
        + Bcolors.ENDC
    )
    print(Bcolors.LISTING + f"Average imdbRating : {average_rating:.1f}" + Bcolors.ENDC)
    print(Bcolors.LISTING + f"Median imdbRating  : {median_rating:.1f}" + Bcolors.ENDC)
    print(Bcolors.LISTING + f"Best movie         : {best}, {max_rat:.1f}" + Bcolors.ENDC)
    print(Bcolors.LISTING + f"Worst movie        : {worst}, {min_rat:.1f}" + Bcolors.ENDC)
    print(Bcolors.ENDC)
