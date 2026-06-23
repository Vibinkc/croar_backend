import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

oxylabs_username = os.getenv("OXYLABS_USERNAME")
oxylabs_password = os.getenv("OXYLABS_PASSWORD")


def test_oxylabs_universal_search():
    payload = {"source": "universal", "url": "https://api.github.com/search/users?q=developer"}

    response = requests.post(
        "https://realtime.oxylabs.io/v1/queries", auth=(oxylabs_username, oxylabs_password), json=payload
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            content = data["results"][0].get("content", "")
            parsed = json.loads(content)
            print("Found items:", len(parsed.get("items", [])))
            if parsed.get("items"):
                print("First item login:", parsed["items"][0]["login"])
    else:
        print("Error:", response.text)


if __name__ == "__main__":
    test_oxylabs_universal_search()
