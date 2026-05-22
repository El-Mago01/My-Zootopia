# import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text


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


# Define the database URL
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "movies.db"
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"
DEBUG = True
# Create the engine
# engine = create_engine(DB_URL, echo=DEBUG)
engine = create_engine(DB_URL)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            imdbID TEXT NOT NULL,
            title TEXT NOT NULL,
            year TEXT NOT NULL,
            imdbRating REAL NOT NULL,
            poster TEXT,
            note TEXT,
            country TEXT
        )
    """))
    connection.commit()


def list_all_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT id, imdbID, Title, Year, imdbRating, Poster, note, country, user_id FROM movies"
            )
        )
        movies = result.fetchall()
    return movies


def list_movies(user_id: int):
    """Retrieve all movies from the database that matches the user_id."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT id, imdbID, Title, Year, imdbRating, Poster, note, country, user_id FROM movies WHERE user_id = :user_id"
            ),
            {"user_id": user_id},
        )
        movies = result.fetchall()
    # print(movies)
    return movies


# pylint: disable=invalid-name
def add_movie(movie: dict, user_id: int) -> bool:
    """Add a movie to the database."""

    imdbID = movie["imdbID"]
    title = movie["Title"]
    year = movie["Year"]
    rating = movie["Rating"]
    poster = movie["Poster"]
    country = movie["Country"]
    with engine.connect() as conn:
        try:
            print(BColors.LISTING + f"Inserting movie {title} into the database")
            params = {
                "user_id": user_id,
                "imdbID": imdbID,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster,
                "country": country,
            }
            conn.execute(
                text(
                    "INSERT INTO movies (user_id, imdbID, Title, Year, imdbRating, Poster, Country) "
                    "VALUES (:user_id, :imdbID, :title, :year, :rating, :poster, :country)"
                ),
                params,
            )
            conn.commit()
            # print(BColors.LISTING + f"Movie '{title}' added successfully." + BColors.ENDC)
            return True
        # Catch any exception that can occur results in movie not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(
                BColors.FAIL + f"Error during storage of the movie: {e}" + BColors.ENDC
            )
            return False


def delete_movie(movie_id: int, title: str, user_id: int) -> bool:
    """Delete a movie from the database."""
    with engine.connect() as conn:
        try:
            print(
                BColors.LISTING
                + f"Deleting movie {title} with ID {movie_id} from the database for user_id {user_id}"
            )
            conn.execute(
                text("DELETE FROM movies WHERE ID = :id AND user_id = :user_id"),
                {"id": movie_id, "user_id": user_id},
            )
            conn.commit()
            print(
                BColors.LISTING
                + f"Movie '{title}' deleted successfully."
                + BColors.ENDC
            )
        # Catch any exception that can occur results in movie not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
            return False
    return True


def update_movie(movie_id: int, new_note: str, title: str) -> bool:
    """Update a movie's rating in the database."""
    with engine.connect() as conn:
        try:
            print(
                BColors.LISTING
                + f"Updating movie {title} with ID {movie_id} from the database "
                + f"with the following note: \n{new_note}"
                + BColors.ENDC
            )
            conn.execute(
                text("UPDATE movies SET note = :note WHERE id = :id"),
                {"id": movie_id, "note": new_note},
            )
            conn.commit()
            # print(BColors.LISTING + f"Movie '{title}' updated successfully." + BColors.ENDC)
        # Catch any exception that can occur results in movie not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
            return False
    return True


def search_movie(title: str, user_id: int, match_type: int = 0) -> dict:
    """
    Search for a movie from the database.

    searches for movies in the dict using the search_string and 4 variants
    expressed by match_type (int)
    match_type 0 => exact match, and case-sensitive
    match_type 1 => exact match but case-insensitive
    match_type 2 => matching characters, but case-insensitive and stripped
    match_type 3 => fuzzy matching# pylint: disable=invalid-name
    """

    SEARCH_QUERY_0 = (
        "SELECT id, imdbID, title, year, imdbRating, poster FROM movies "
        "WHERE title = :title AND user_id = :user_id"
    )
    params_0 = {"title": title, "user_id": user_id}
    SEARCH_QUERY_1 = (
        "SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
        "WHERE LOWER(title) = :title AND user_id = :user_id"
    )
    params_1 = {"title": title.lower(), "user_id": user_id}
    SEARCH_QUERY_2 = (
        "SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
        "WHERE REPLACE(LOWER(title),' ','') = :title AND user_id = :user_id"
    )
    params_2 = {"title": title.lower().replace(" ", ""), "user_id": user_id}
    SEARCH_QUERY_3 = (
        "SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
        "WHERE LOWER(title) LIKE :title AND user_id = :user_id"
    )
    params_3 = {"title": f"%{title.lower()}%", "user_id": user_id}

    with engine.connect() as conn:
        try:
            print(
                BColors.LISTING
                + f"Searching for movie {title} into the database"
                + BColors.ENDC
            )
            if match_type == 0:
                result = conn.execute(text(SEARCH_QUERY_0), params_0)
            elif match_type == 1:
                result = conn.execute(text(SEARCH_QUERY_1), params_1)
            elif match_type == 2:
                result = conn.execute(text(SEARCH_QUERY_2), params_2)
            elif match_type == 3:
                result = conn.execute(text(SEARCH_QUERY_3), params_3)
            else:
                raise ReferenceError("Search function not implemented")
            conn.commit()
        # pylint: disable=broad-exception-caught
        # Any type of connection failure is caught
        except Exception as e:
            print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
            return {}
        res = result.fetchall()
        # print(f"the search function will return this: {res}")
    return res


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

    found_movies = search_movie("    The    hulk   ", 1, 2)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies = search_movie("hulk", 1, 3)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies = search_movie("Bee Bulk", 1, 1)
    print(f" This/these movie(s) were found{found_movies}")


if __name__ == "__main__":
    main()
