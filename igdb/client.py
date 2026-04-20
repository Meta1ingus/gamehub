import os
import requests
from dotenv import load_dotenv

load_dotenv()

class IGDBClient:
    BASE_URL = "https://api.igdb.com/v4"

    def __init__(self):
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.access_token = os.getenv("IGDB_ACCESS_TOKEN")

        if not self.client_id or not self.access_token:
            raise ValueError("Missing IGDB credentials in .env")

    def query(self, endpoint: str, query: str):
        """
        Send a POST request to an IGDB endpoint with the given query.
        """
        url = f"{self.BASE_URL}/{endpoint}"

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.post(url, headers=headers, data=query)

        if response.status_code != 200:
            raise Exception(
                f"IGDB API error {response.status_code}: {response.text}"
            )

        return response.json()
