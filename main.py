import requests
import json
import datetime
import os


def get_directors_movies(api_key, director_name):
    base_url = "https://api.themoviedb.org/3/search/person?api_key="
    search_url =  base_url + api_key + "&query=" + director_name

    response = requests.get(search_url) # Make a request to the API

    if response.status_code == 200:
        # Success
        json_data = response.json()

        director_id = json_data["results"][0]["id"] # Get the director ID

        # Get the movies
        movies_url = "https://api.themoviedb.org/3/person/" + str(director_id) + "/movie_credits?api_key=" + api_key
        movies_response = requests.get(movies_url)

        if movies_response.status_code == 200:
            movies_json_data = movies_response.json()
            # director_movies = [movie["title"] for movie in movies_json_data["crew"] if movie["job"] == "Director"]
            new_movies = []
            for movie in movies_json_data["crew"]:
                if movie["job"] == "Director":
                    release_date = datetime.datetime.strptime(movie["release_date"], "%Y-%m-%d")
                    if release_date > last_run_time:
                        new_movies.append(movie["title"])
            return new_movies
        else:
            print(f"Error: {movies_response.status_code}")

    else:
        print(f"Error: {response.status_code}")


last_run_file = "/Users/harethhmoud/Desktop/Desktop - Hareths MacBook Pro/Everything/test.txt"

if os.path.exists(last_run_file):
    with open(last_run_file, "r") as file:
        last_run = file.read().strip() # Read the last run time from the file and remove any leading/trailing whitespace
        if last_run: # If the file is not empty
            last_run_time = datetime.datetime.strptime(last_run, "%Y-%m-%d")
        else: # If the file is empty
            last_run_time = datetime.datetime(1900, 1, 1)
else:
    last_run_time = datetime.datetime(1900, 1, 1) # If the file doesn't exist, set the last run time to a long time ago

api_key = "691b722aa9da09fd8591ef7f067b5e07"
director_name = "Christopher Nolan"
movies = get_directors_movies(api_key, director_name)
for title in movies:
    print(title)

with open(last_run_file, "w") as file: # Write the current time to the file
    file.write(datetime.datetime.now().strftime("%Y-%m-%d"))












