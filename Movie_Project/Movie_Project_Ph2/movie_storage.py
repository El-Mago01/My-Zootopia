import movie_storage_sql as mss
import movie_storage_json as msj

STORAGE = {"SQL" : "SQL",
           "JSON" : "JSON"
           }
SELECTED_STORAGE = STORAGE["JSON"]


def fetch_all_movies():
    """Retrieve all movies from the database."""
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.fetch_all_movies()
    else:
        return mss.fetch_all_movies()


def fetch_movies(user_id: int):
    """Retrieve all movies from the database that matches the user_id."""
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.fetch_movies(user_id)
    else:
        return mss.fetch_movies(user_id)


def add_movie(movie: dict, user_id: int) -> bool:
    """Add a movie to the database."""
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.add_movie(movie, user_id)
    else:
        return mss.add_movie(movie, user_id)


def delete_movie(movie_id: int, title: str, user_id: int) -> bool:
    """Delete a movie from the database."""
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.delete_movie(movie_id, title, user_id)
    else:
        return mss.delete_movie(movie_id, title, user_id)


def update_movie(movie_id: int, new_note: str, title: str) -> bool:
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.update_movie(movie_id, new_note, title)
    else:
        return mss.update_movie(movie_id, new_note, title)

def search_movie(title: str, user_id: int, match_type: int = 0) -> dict:
    """
    """
    if SELECTED_STORAGE == STORAGE["JSON"]:
        return msj.search_movie(title, user_id, match_type)
    else:
        return mss.search_movie(title, user_id, match_type)
