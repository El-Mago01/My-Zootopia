import os
import json
from user_interface import Bcolors


STORAGE_DIR = "data"
MOVIE_STORAGE = os.path.join(STORAGE_DIR, "movies.json")


def fetch_movie_from_storage() -> list:
    """Retrieve all movies from the database.
    Return:
    # Returned movie: positions per movie:
    # 0. id
    # 1. user_id
    # 2. imdbID
    # 3. Title
    # 4. Year
    # 5. Rating
    # 6. Poster
    # 7. Note
    # 8. Country
    """
    try:
        with open(MOVIE_STORAGE, "r") as fileobj:
            content = fileobj.read()
        if content:
            movies = json.loads(content)
        else:
            movies = []
    except FileNotFoundError:
        movies = []
    except OSError as e:
        print(f"{Bcolors.FAIL}Could not store movie data. Please contact your "
              f"adminstrator. \nError: {e} {Bcolors.ENDC}")
        movies = []
    return movies


def store_movies(content: list) -> bool:
    """Store movie data in the JSON archive.
    param: the content of all the movies to store
    """
    content_to_write = json.dumps(content)
    if os.path.exists(MOVIE_STORAGE):
        try:
            with open(MOVIE_STORAGE, "w") as fileobj:
                fileobj.write(content_to_write)
        except OSError as e:
            print(f"{Bcolors.FAIL}Could not store movie data. Please contact your "
                  f"adminstrator. \nError: {e} {Bcolors.ENDC}")
            return False
    else:
        try:
            with open(MOVIE_STORAGE, "w") as fileobj:
                fileobj.write(content_to_write)
        except OSError as e:
            print(f"{Bcolors.FAIL}Could not store movie data. Please contact your "
                  f"adminstrator. \nError: {e} {Bcolors.ENDC}")
            print("Here is the movie data that might be lost :")
            for movie in content:
                print(movie)
            return False
    return True

def append_movie_to_storage(movie_data: list) -> bool:
    """Store the new movie data in the content for the JSON archive.
    param: tthe movie to stor
    return: Successful or failed storage

    # Storage positions:
    # 0. id
    # 1. user_id
    # 2. imdbID
    # 3. Title
    # 4. Year
    # 5. Rating
    # 6. Poster
    # 7. Note
    # 8. Country
    """
    current_movies = fetch_movie_from_storage()
    updated_movies = []
    if len(current_movies) == 0: #The first movie in the DB
        # Insert an identifier for this movie
        movie_data.insert(0,0)
        updated_movies.append(movie_data)
    else:
        # look for the last stored entry in the DB and order it based on movie_id
        # Create and identifier by finding the last entry and add 1 to it's id
        updated_movies = sorted(current_movies)
        # print(updated_movies)
        movie_data.insert(0, current_movies[-1][0] + 1)
        updated_movies.append(movie_data)
    return store_movies(updated_movies)



def fetch_all_movies():
    """Retrieve all movies from the JSON archive.
    # Returned movie: positions per movie:

    # 0. id
    # 1. user_id
    # 2. imdbID
    # 3. Title
    # 4. Year
    # 5. Rating
    # 6. Poster
    # 7. Note
    # 8. Country
    """

    available_movies = fetch_movie_from_storage()
    return available_movies


def fetch_movies(user_id: int):
    """ Fetch all movies from a specific user_id
    # Returned movie: positions per movie:
    # 0. id
    # 1. user_id
    # 2. imdbID
    # 3. Title
    # 4. Year
    # 5. Rating
    # 6. Poster
    # 7. Note
    # 8. Country
    """
    movies = []
    available_movies = fetch_movie_from_storage()
    # print("Fetching the movies for: ", user_id)
    for movie in available_movies:
        if movie[1] == user_id:
            movies.append(movie)
    return movies


# pylint: disable=invalid-name
def add_movie(movie: dict, user_id: int) -> bool:
    """Add a movie to the database.
    param: movie
    param: user_id
    Return: Successful or failed storage"""
    # print("Movie to add", movie)
    # print("for user", user_id)
    movie_list = [
        user_id,
        movie["imdbID"],
        movie["Title"],
        movie["Year"],
        movie["Rating"],
        movie["Poster"],
        "", #The Note, can be used later
        movie["Country"]
    ]
    return append_movie_to_storage(movie_list)


def delete_movie(movie_id: int, title: str, user_id: int) -> bool:
    """Delete a movie from the database.
    param: movie_id
    param: the title
    param: user_id
    Return: Successful or failed deletion"""

    current_movies = fetch_movie_from_storage()
    if len(current_movies) == 0:  # If there is no movie yet, nothing is deleted.
        return False
    print(
        Bcolors.LISTING
        + f"Deleting movie {title} with ID {movie_id} from the database for user_id {user_id}"
    )
    # pop the film to be deleted
    movie_deleted = False
    for movie in current_movies:
        if movie[0] == movie_id:
            current_movies.remove(movie)
            movie_deleted = True
            break
    if movie_deleted and store_movies(current_movies):
        print(
            Bcolors.LISTING
            + f"Movie '{title}' deleted successfully."
            + Bcolors.ENDC
        )
        return True
    return False


def update_movie(movie_id: int, new_note: str, title: str) -> bool:
    """Update a movie's note in the database.
    param: movie_id
    param: the title
    param: user_id
    Return: Successful or failed update
    """
    current_movies = fetch_movie_from_storage()
    if len(current_movies) == 0:  # If there is no movie yet, nothing is updated.
        return False

    # Find the film to be updated
    movie_updated = False
    for movie in current_movies:
        # print("movie, movie_id",movie, movie_id)
        if movie[0] == movie_id:
            movie[7] = new_note
            movie_updated = True
            break
    if not movie_updated:
        print(
            Bcolors.WARNING
            + f"Movie '{title}' not found. Note update failed"
            + Bcolors.ENDC
        )

    if not store_movies(current_movies):
        print(
            Bcolors.WARNING
            + f"Movies '{title}' could not be stored"
            + Bcolors.ENDC
        )
        return False
    return True


def search_movie(title: str, user_id: int, match_type: int = 0) -> list:
    """
    Search for a movie from the JSON database.

    searches for movies in the dict using the search_string and 4 variants
    expressed by match_type (int)
    match_type 0 => exact match, and case-sensitive
    match_type 1 => exact match but case-insensitive
    match_type 2 => matching characters, but case-insensitive and stripped
    match_type 3 => fuzzy matching# pylint: disable=invalid-name
    """
    all_user_movies = fetch_movies(user_id)
    # print(all_user_movies)
    found_movies = []
    for movie in all_user_movies:
        movie_tuple = (
            movie[0],
            movie[1],
            movie[2],
            movie[3],
            movie[4],
            movie[5],
            movie[6],
            movie[7],
            movie[8]
                )
        if match_type == 0:
            if movie[3] == title:
                found_movies.append(movie_tuple)
        if match_type == 1:
            if movie[3].lower() == title.lower():
                found_movies.append(movie_tuple)
        if match_type == 2:
            if title.lower() in movie[3].lower().strip():
                found_movies.append(movie_tuple)
        if match_type == 3:
            if title.lower() in movie[3].lower().strip():
                found_movies.append(movie_tuple)
    # print(f"the search function will return this: {found_movies}")

    return found_movies


def main():
    """
    Contains some basic tests to test the working of the database
    :return:
    """
    # found_movies=search_movie("The Hulk",0)
    # print(f" This/these movie(s) were found: {found_movies}")
    #
    # found_movies=search_movie("The hulk",1)
    # print(f" This/these movie(s) were found{found_movies}")

    # all_movies = fetch_all_movies()
    # print(all_movies)

    # found_movies = search_movie("    The    hulk   ", 1, 2)
    # print(f" This/these movie(s) were found{found_movies}")
    #
    # found_movies = search_movie("hulk", 1, 3)
    # print(f" This/these movie(s) were found{found_movies}")
    # for movie in found_movies:
    #     print(type(movie))
    # found_movies = search_movie("Bee Bulk", 1, 1)
    # print(f" This/these movie(s) were found{found_movies}")
    # print(type(found_movies))



if __name__ == "__main__":
    main()
