import requests
import json
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class DirectorMoviesNotifier:
    BASE_URL = "https://api.themoviedb.org/3/search/person?api_key="

    def __init__(self, config):
        self.api_key = config["API_KEY"]
        self.email_username = config["EMAIL_USERNAME"]
        self.email_password = config["EMAIL_PASSWORD"]
        self.directors = self._load_directors()

    @staticmethod
    def _load_directors():
        with open("directors.txt", "r") as director_file:
            return director_file.read().splitlines()

    def get_directors_movies(self, director_name, last_run_time):
        search_url = self.BASE_URL + self.api_key + "&query=" + director_name

        response = requests.get(search_url)  # Make a request to the API

        if response.status_code == 200:
            # Success
            json_data = response.json()

            director_id = json_data["results"][0]["id"]  # Get the director ID

            # Get the movies
            movies_url = "https://api.themoviedb.org/3/person/" + str(director_id) + "/movie_credits?api_key=" \
                         + self.api_key
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

    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_username
        msg['To'] = self.email_username
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            print("Successfully sent email to %s." % (msg['To']))
        except Exception as e:
            print("Failed to send email: %s" % str(e))

    def notify_new_movies(self, last_run_time):
        new_movies_info = []
        for director in self.directors:
            movies = self.get_directors_movies(director, last_run_time)
            for title in movies:
                new_movies_info.append(f"{director}: {title}")
        if new_movies_info:
            self.send_email("New Movies", "\n".join(new_movies_info))


def main():
    with open("config.json", "r") as file:
        config = json.load(file)

    notifier = DirectorMoviesNotifier(config)

    last_run_file = config["LAST_RUN_FILE_PATH"]

    if os.path.exists(last_run_file):
        with open(last_run_file, "r") as file:
            last_run = file.read().strip()
            if last_run:
                last_run_time = datetime.datetime.strptime(last_run, "%Y-%m-%d")
            else:
                last_run_time = datetime.datetime(1900, 1, 1)
    else:
        last_run_time = datetime.datetime(1900, 1, 1)

    notifier.notify_new_movies(last_run_time)

    with open(last_run_file, "w") as file:
        file.write(datetime.datetime.now().strftime("%Y-%m-%d"))


if __name__ == "__main__":
    main()
