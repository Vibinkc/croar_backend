import json

import requests


def test_backend_api(query, platform):
    url = "http://localhost:8000/api/v1/enterprise/sourcing/search"
    params = {"q": query, "platform": platform, "page": 1, "page_size": 15}
    print(f"DEBUG: Calling {url} with {params}")
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"DEBUG: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Received {len(data)} results")
            if len(data) > 0:
                print("DEBUG: Sample result:")
                print(json.dumps(data[0], indent=2))
        else:
            print(f"DEBUG: Error response: {response.text}")
    except Exception as e:
        print(f"DEBUG: Connection error: {e}")


if __name__ == "__main__":
    test_backend_api("UI UX", "behance")
