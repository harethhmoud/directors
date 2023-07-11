import requests
import json
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open("directors.txt", "r") as director_file:
    directors = director_file.read().splitlines()


def get_directors_movies(director_name):
    base_url = "https://api.themoviedb.org/3/search/person?api_key="
    search_url = base_url + api_key + "&query=" + director_name

    response = requests.get(search_url)  # Make a request to the API

    if response.status_code == 200:
        # Success
        json_data = response.json()

        director_id = json_data["results"][0]["id"]  # Get the director ID

        # Get the movies
        movies_url = "https://api.themoviedb.org/3/person/" + str(director_id) + "/movie_credits?api_key=" + api_key
        movies_response = requests.get(movies_url)

        if movies_response.status_code == 200:
            movies_json_data = movies_response.json()
            # director_movies = [movie["title"] for movie in movies_json_data["crew"] if movie["job"] == "Director"]
            new_movies = []
            for movie in movies_json_data["crew"]:
                if movie["job"] == "Director":
                    if "release_date" in movie and movie[
                        "release_date"]:  # Check if a release date exists and is not empty
                        release_date = datetime.datetime.strptime(movie["release_date"], "%Y-%m-%d")
                        if release_date > last_run_time:
                            new_movies.append(movie["title"])
            return new_movies
        else:
            print(f"Error: {movies_response.status_code}")

    else:
        print(f"Error: {response.status_code}")


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_username
    msg['To'] = email_username
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(email_username, email_password)
        server.send_message(msg)
        server.quit()
        print("Successfully sent email to %s:" % (msg['To']))
    except Exception as e:
        print("Failed to send email: %s" % str(e))


last_run_file = "/Users/harethhmoud/Desktop/Desktop - Hareths MacBook Pro/Everything/test.txt"

if os.path.exists(last_run_file):
    with open(last_run_file, "r") as file:
        last_run = file.read().strip()  # Read the last run time from the file and remove any leading/trailing whitespace
        if last_run:  # If the file is not empty
            last_run_time = datetime.datetime.strptime(last_run, "%Y-%m-%d")  # Convert the string to a datetime object
        else:  # If the file is empty
            last_run_time = datetime.datetime(1900, 1, 1)
else:
    last_run_time = datetime.datetime(1900, 1, 1)  # If the file doesn't exist, set the last run time to a long time ago

with open("config.json", "r") as file:
    config = json.load(file)

api_key = config["API_KEY"]
email_username = config["EMAIL_USERNAME"]
email_password = config["EMAIL_PASSWORD"]
for director in directors:
    movies = get_directors_movies(director)
    for title in movies:
        # print(title)
        send_email('New movie from ' + director, title)

with open(last_run_file, "w") as file:  # Write the current time to the file
    file.write(datetime.datetime.now().strftime("%Y-%m-%d"))
