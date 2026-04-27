import os
from pathlib import Path

MOVIES="_static/mago_favorite_movies.html"

def load_html_file(file_path):
    with open(file_path, "r") as handle:
        return handle.read()
    
def write_to_new_html_file(html_file, content):
    with open(html_file, "w") as f:
        f.write(content)
        print(f'File stored in:{Path(__file__).parent.joinpath(f.name)}')

def generate_grid(movies: list): #A list of tuples with the movies 
    """
    Generates a grid with the movies in the MOVIES file.
    """
    grid=""
    for movie in movies:
        grid+=f"""
            <li>
                <div class="movie">
                    <img class="movie-poster" src="{movie[5]}" alt="{movie[2]} poster">
                    <div class="movie-title">{movie[2]}</div>
                    <div class="movie-year">{movie[3]}</div>
                </div>
            </li>
        """
    return grid
    
def generate_website(movies, username):
    """
    Generates a website with the movies in the MOVIES file.
    """  
    PAGE_TITLE=f"{username}'s Favorite Films and Series"
    MOVIES=f"_static/{username}_favorite_movies.html"
    TEMPLATE="_static/index_template.html"
    _TITLE_="__TEMPLATE_TITLE__"
    _MOVIE_GRID_="__TEMPLATE_MOVIE_GRID__"
    content=load_html_file(TEMPLATE)
    content=content.replace(_TITLE_, PAGE_TITLE) 
    content=content.replace(_MOVIE_GRID_, generate_grid(movies))   
    write_to_new_html_file(MOVIES, content)   