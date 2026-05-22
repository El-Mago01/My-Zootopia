Why movies-app
With movies=app you can add, list and delete your favorite favorite 
movies with a simple menu. After storage, you can get a random
film recommendation. 

The movies stored contain a title, year, imdbRating, a Poster link.
With the imdbRating you can get statistics, like which one of your 
favorites is considered the best and worst. It further enables you 
analyze the ratings in a histogram. On top of all these wonderful
features, you can also get analysis of the imdbRatings in form
of the mean and median of these ratings. 

Installation:
Ensure python is installed on your device
Install the movies installation package 

Go to the newly installed base folder

Ensure the following files are in your folder:
- movies.py
- movie-storage-sql.py
- movie_web_generator.py
- movie_detail_fetcher.py
In the installed base folder, create a data folder

Usage:
Just run the program:
python movies.py
Any generated web site will be stored folder _static
histogram is stored in the base folder

The following menu should become visible:
1 - List movies
2 - Add movie
3 - Delete movie
4 - Show movie statistics
5 - Select a movie randomly
6 - Search by title
7 - Movies sorted by rating
8 - Create rating histogram
9 - Gereate the website
0 - Exit