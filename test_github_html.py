import os

import requests
from dotenv import load_dotenv

load_dotenv()


def test():
    username = os.getenv("OXYLABS_USERNAME")
    password = os.getenv("OXYLABS_PASSWORD")

    payload = {"source": "universal", "url": "https://github.com/developerrahulofficial"}

    res = requests.post("https://realtime.oxylabs.io/v1/queries", auth=(username, password), json=payload)
    data = res.json()
    if data.get("results"):
        print(data["results"][0]["content"][:500])


if __name__ == "__main__":
    test()
