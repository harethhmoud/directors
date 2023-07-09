import requests
import json


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
            director_movies = [movie["title"] for movie in movies_json_data["crew"] if movie["job"] == "Director"]
            return director_movies
        else:
            print(f"Error: {movies_response.status_code}")

    else:
        print(f"Error: {response.status_code}")


api_key = "691b722aa9da09fd8591ef7f067b5e07"
director_name = "Christopher Nolan"
movies = get_directors_movies(api_key, director_name)
for title in movies:
    print(title)











