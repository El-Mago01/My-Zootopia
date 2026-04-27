# import sqlite3
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/movies.db"
DEBUG = True
# Create the engine
engine = create_engine(DB_URL, echo=DEBUG)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdbID TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            year TEXT NOT NULL,
            imdbRating REAL NOT NULL,
            poster TEXT
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, imdbID, Title, Year, imdbRating, Poster FROM movies"))
        movies = result.fetchall()
    print(movies)
    print(type(movies))
    return movies

# pylint: disable=invalid-name
def add_movie(movie: dict) -> bool:
    """Add a movie to the database."""

    imdbID = movie['imdbID']
    title = movie['Title']
    year = movie['Year']
    rating = movie['Rating']
    poster = movie['Poster']
    print("Poster:", poster)
    with engine.connect() as conn:
        try:
            print(f"Inserting movie {title} into the database")
            params = {
                "imdbID": imdbID,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster}
            conn.execute(
                text(
                    "INSERT INTO movies (imdbID, Title, Year, imdbRating, Poster) "
                    "VALUES (:imdbID, :title, :year, :rating, :poster)"),
                params)
            conn.commit()
            print(f"Movie '{title}' added successfully.")
            return True
        # Catch any exception that can occur results in movie not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Error during storage of the movie: {e}")
            return False


def delete_movie(movie_id, title) -> bool:
    """Delete a movie from the database."""
    with engine.connect() as conn:
        try:
            print(
                f"Deleting movie {title} with ID {movie_id} from the database")
            conn.execute(text("DELETE FROM movies WHERE ID = :id"),
                               {"id": movie_id})
            conn.commit()
            print(f"Movie '{title}' deleted successfully.")
        # Catch any exception that can occur results in movie not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True

# def update_movie(movie_id, new_rating, title):
#     """Update a movie's rating in the database."""
#     with engine.connect() as connection:
#         try:
#             print(f"updating movie {title} with ID {movie_id} from the database")
#             connection.execute(text("UPDATE movies SET rating = :rating WHERE id = :id"),
#                                {"id": movie_id, "rating": new_rating})
#             connection.commit()
#             print(f"Movie '{title}' updated successfully.")
#         except Exception as e:
#             print(f"Error: {e}")
#             return False
#     return True


# searches for movies in the dict using the search_string and 4 variants
# expressed by match_type (int)
#   match_type 0 => exact match, and case-sensitive
#   match_type 1 => exact match but case-insensitive
#   match_type 2 => matching characters, but case-insensitive and stripped
#   match_type 3 => fuzzy matching
# pylint: disable=invalid-name
def search_movie(title, match_type: int = 0) -> dict:
    """Search for a movie from the database."""

    SEARCH_QUERY_0 = ("SELECT id,imdbID, title, year, imdbRating,poster FROM movies "
                      "WHERE title = :title")
    params_0 = {"title": title}
    SEARCH_QUERY_1 = ("SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
                      "WHERE LOWER(title) = :title")
    params_1 = {"title": title.lower()}
    SEARCH_QUERY_2 = ("SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
                      "WHERE REPLACE(LOWER(title),' ','') = :title")
    params_2 = {"title": title.lower().replace(' ', '')}
    SEARCH_QUERY_3 = ("SELECT id,imdbID, title, year, imdbRating, poster FROM movies "
                      "WHERE LOWER(title) LIKE :title")
    params_3 = {"title": f"%{title.lower()}%"}

    with engine.connect() as conn:
        try:
            print(f"Searching for movie {title} into the database")
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
            print(result)
        # pylint: disable=broad-exception-caught
        # Any type of connection failure is caught
        except Exception as e:
            print(f"Error: {e}")
            return {}
        res = result.fetchall()
        print(f"the search function will return this: {res}")

        print(type(res))
        print(res)
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

    found_movies = search_movie("    The    hulk   ", 2)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies = search_movie("hulk", 3)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies = search_movie("Bee Bulk", 4)
    print(f" This/these movie(s) were found{found_movies}")


if __name__ == '__main__':
    main()
