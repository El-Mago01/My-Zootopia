from sqlalchemy import create_engine,text

# Define the database URL
DB_URL = "sqlite:///movies.db"
DEBUG=True
# Create the engine
engine = create_engine(DB_URL, echo=DEBUG)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL
        )
    """))
    connection.commit()

def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2]} for row in movies}

def add_movie(title, year, rating):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            print(f"Inserting movie {title} into the database")
            connection.execute(text("INSERT INTO movies (title, year, rating) VALUES (:title, :year, :rating)"),
                               {"title": title, "year": year, "rating": rating})
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")

def delete_movie(movie_id, title) -> bool:
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            print(f"Deleting movie {title} with ID {movie_id} from the database")
            connection.execute(text("DELETE FROM movies WHERE id = :id"),
                               {"id": movie_id})
            connection.commit()
            print(f"Movie '{title}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True

def update_movie(movie_id, new_rating, title):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            print(f"updating movie {title} with ID {movie_id} from the database")
            connection.execute(text("UPDATE movies SET rating = :rating WHERE id = :id"),
                               {"id": movie_id, "rating": new_rating})
            connection.commit()
            print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True
# searches for movies in the dict using the search_string and 4 variants expressed by match_type (int)
#   match_type 0 => exact match, and case-sensitive
#   match_type 1 => exact match but case-insensitive
#   match_type 2 => matching characters, but case-insensitive and stripped
#   match_type 3 => fuzzy matching
def search_movie(title,match_type:int=0) -> dict:
    """Search for a movie from the database."""

    SEARCH_QUERY_0="SELECT id, title, year, rating FROM movies WHERE title = :title"
    params_0={"title": title}
    SEARCH_QUERY_1="SELECT id, title, year, rating FROM movies WHERE LOWER(title) = :title"
    params_1={"title": title.lower()}
    SEARCH_QUERY_2="SELECT id, title, year, rating FROM movies WHERE REPLACE(LOWER(title),' ','') = :title"
    params_2={"title": title.lower().replace(' ','')}
    SEARCH_QUERY_3="SELECT id, title, year, rating FROM movies WHERE LOWER(title) LIKE :title"
    params_3={"title": f"%{title.lower()}%"}


    with engine.connect() as connection:
        try:
            print(f"Searching for movie {title} into the database")
            if match_type == 0:
                result=connection.execute(text(SEARCH_QUERY_0), params_0)
            elif match_type == 1:
                result=connection.execute(text(SEARCH_QUERY_1),params_1)
            elif match_type == 2:
                result=connection.execute(text(SEARCH_QUERY_2),params_2)
            elif match_type == 3:
                result=connection.execute(text(SEARCH_QUERY_3),params_3)
            else:
                raise ReferenceError("Search function not implemented")
            connection.commit()
            print(result)
        except Exception as e:
            print(f"Error: {e}")
            return {}
        res=result.fetchall()
        print(f"the search function will return this: {res}")

        print(type(res))
        print(res)
    return res


def main():
    # found_movies=search_movie("The Hulk",0)
    # print(f" This/these movie(s) were found: {found_movies}")
    #
    # found_movies=search_movie("The hulk",1)
    # print(f" This/these movie(s) were found{found_movies}")

    found_movies=search_movie("    The    hulk   ",2)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies=search_movie("hulk",3)
    print(f" This/these movie(s) were found{found_movies}")

    found_movies=search_movie("Bee Bulk",4)
    print(f" This/these movie(s) were found{found_movies}")

if __name__ == '__main__':
    main()
