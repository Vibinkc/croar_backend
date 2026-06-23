import random

import requests
from bs4 import BeautifulSoup


def search(query, site_domain, result_pattern, location=None):
    search_url = "https://duckduckgo.com/html/"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]

    full_query = f'site:{site_domain} "{query}"'
    if location:
        full_query += f' "{location}"'

    session = requests.Session()
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    print(f"DEBUG: Testing {full_query}")
    try:
        session.get("https://duckduckgo.com/", headers=headers, timeout=5)
        response = session.get(search_url, params={"q": full_query}, headers=headers, timeout=10)
        print(f"DEBUG: Status {response.status_code}")

        if response.status_code != 200:
            print("DEBUG: Fallback to Lite")
            lite_url = "https://duckduckgo.com/lite/"
            response = session.get(lite_url, params={"q": full_query}, headers=headers, timeout=10)
            print(f"DEBUG LITE: Status {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="result__a") or soup.find_all("a", class_="result-link")
            print(f"DEBUG: Found {len(links)} links")
            for link in links:
                print(f"DEBUG: Link: {link.get('href')}")
    except Exception as e:
        print(f"DEBUG: Error {e}")


if __name__ == "__main__":
    search("React Developer", "linkedin.com/in/", "linkedin.com/in/")
